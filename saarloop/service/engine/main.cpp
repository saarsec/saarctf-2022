#include <iostream>
#include <json/json.h>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <sndfile.hh>
#include <algorithm>

const int SAMPLE_RATE = 11025;
const int MAX_SAMPLE_SIZE = 16384;
const double REF_FREQ = 175.0;
const double REF_NOTE = 53;
const std::filesystem::path DATA_DIR("./data");
const std::filesystem::path SAMPLE_DIR("samples/");
const std::filesystem::path SYNTH_DIR("synths/");

struct {
    double bpm;
} SONG_INFO;

size_t NOTE_BUFFER_LEN = MAX_SAMPLE_SIZE;
unsigned char NOTE_BUFFER[MAX_SAMPLE_SIZE];
char USERNAME[64];

double saw(double x) {
    return fmod(x / M_PI, 2) - 1;
}

double square(double x) {
    return fmod(x / M_PI, 2) < 1 ? 1 : -1;
}

bool filename_is_valid(const std::string &str) {
    return std::find_if(str.begin(), str.end(),
                        [](char c) { return !(isalnum(c) || (c == '-') || (c == '_')); }) == str.end();
}

enum osc_type {
    SIN, SAW, SQUARE
};

__attribute__((noinline))
void
load_sample(unsigned char *buffer, size_t *buflen, const std::filesystem::path &path, const std::string &sample_id) {
    if (!filename_is_valid(sample_id)) {
        std::cerr << "Error, invalid sample " << sample_id << std::endl;
        throw;
    }
    auto load_path = path / std::filesystem::path(sample_id + ".wav");
    if (!is_regular_file(load_path)) {
        std::cerr << "Error, file " << load_path << " does not exist!" << std::endl;
        throw;
    }
    //std::cerr << "Will load sample from " << load_path << std::endl;

    SF_INFO sf_info = {0};
    SNDFILE *input_file = sf_open(load_path.c_str(), SFM_READ, &sf_info);

    if (sf_info.frames > MAX_SAMPLE_SIZE) {
        std::cerr << "Error, sample file " << load_path << " too big!" << std::endl;
        throw;
    }

    if (sf_info.channels > 1 || sf_info.samplerate != SAMPLE_RATE ||
        sf_info.format != (SF_FORMAT_WAV | SF_FORMAT_PCM_U8)) {
        std::cerr << "Error, sample file " << load_path << " has invalid format!" << std::endl;
        throw;
    }

    sf_read_raw(input_file, buffer, sf_info.frames);
    *buflen = sf_info.frames;

    sf_close(input_file);

}

__attribute__((noinline))
void audio_add(unsigned char *dst, size_t dst_size, size_t offset, const unsigned char *src, size_t size) {
    for (size_t i = 0; i < size; i++) {
        dst[(offset + i)%dst_size] += src[i] - 0x80;
    }
}

__attribute__((noinline))
double to_double(unsigned char x) {
    //return (x - 0x80) / 127.0;
    return 2 * x / 255.0 - 1.0;
}

__attribute__((noinline))
unsigned char to_u8(double x) {
    //return roundl(x * 127.0) + 0x80;
    return roundl(255.0 * (x + 1.0) / 2.0);
}

__attribute__((noinline))
void adjust_volume(unsigned char *buffer, size_t size, double volume) {
    for (size_t i = 0; i < size; i++) {
        buffer[i] = to_u8(to_double(buffer[i]) * volume);
    }
}

__attribute__((noinline))
void adsr(unsigned char *buffer, size_t size, size_t a, size_t d, double s, size_t r) {
    size_t i = 0;
    for (; i < a && i < size - r; i++) {
        double x = (1.0 * i) / a;
        buffer[i] = to_u8(to_double(buffer[i]) * x);
    }
    for (; i < a + d && i < size - r; i++) {
        double x = ((i - a) * 1.0 / d);
        x = 1.0 * (1 - x) + s * x;
        buffer[i] = to_u8(to_double(buffer[i]) * x);
    }
    for (; i < size - r; i++) {
        buffer[i] = to_u8(to_double(buffer[i]) * s);
    }
    for (; i < size; i++) {
        double x = (((size - i) * 1.0) / r) * s;
        buffer[i] = to_u8(to_double(buffer[i]) * x);
    }
}

__attribute__((noinline))
std::vector<std::tuple<osc_type, double, double, double>>
load_synth(const std::filesystem::path &path, const std::string &sample_id) {
    if (!filename_is_valid(sample_id)) {
        std::cerr << "Error, invalid synth " << sample_id << std::endl;
        throw;
    }
    auto load_path = path / std::filesystem::path(sample_id + ".json");
    //std::cerr << "Will load synth from " << load_path << std::endl;

    std::vector<std::tuple<osc_type, double, double, double>> synth_stack;

    std::ifstream synth_file(load_path);
    Json::Value synth_info;
    synth_file >> synth_info;

    for (auto &&osc: synth_info["oscs"]) {
        osc_type osc_type;
        if (osc["type"] == "SINE") {
            osc_type = SIN;
        } else if (osc["type"] == "SAW") {
            osc_type = SAW;
        } else if (osc["type"] == "SQUARE") {
            osc_type = SQUARE;
        } else {
            std::cerr << "Error, unknown oscillator type " << osc["type"] << std::endl;
            throw;
        }
        synth_stack.emplace_back(
                std::make_tuple(osc_type, osc["vol"].asDouble(), osc["fmult"].asDouble(), osc["phase"].asDouble()));
    }

    return synth_stack;
}

__attribute__((noinline))
void render_note(unsigned char *buffer, size_t *buflen, const Json::Value &note_info,
                 std::vector<std::tuple<osc_type, double, double, double>> &synth_stack) {

    *buflen = lround(60.0 * note_info["d"].asDouble() * SAMPLE_RATE / SONG_INFO.bpm);
    /*
    std::cerr << "Note duration: " << note_info["d"].asDouble() << " beats\n";
    std::cerr << "At " << bpm << " bpm that equals " << (60.0 * note_info["d"].asDouble() / bpm) << " seconds\n";
    std::cerr << "or " << *buflen << " samples" << std::endl;
    */
    double base_freq = REF_FREQ * pow(2, (note_info["p"].asDouble() - REF_NOTE) / 12.0);
    /*
    std::cerr << "MIDI-Note " << note_info["p"].asDouble() << " corresponds to a frequency of " << base_freq << " Hz"
              << std::endl;
    */
    for (size_t i = 0; i < *buflen; i++) {
        double v = 0;
        for (auto &&synth: synth_stack) {
            osc_type osc_type;
            double fmult, vol, phase;
            std::tie(osc_type, vol, fmult, phase) = synth;
            double osc_freq = base_freq * fmult;
            double x = (osc_freq * i / SAMPLE_RATE) * 2.0 * M_PI + phase;
            /*
            std::cerr << "Adding oscillator at " << osc_freq << " Hz, volume " << vol << ", phase-offset " << phase
                      << ", sampling at x:\t" << x << std::endl;
            */
            switch (osc_type) {
                case SIN:
                    v += sin(x) * vol;
                    break;
                case SAW:
                    v += saw(x) * vol;
                    break;
                case SQUARE:
                    v += square(x) * vol;
                    break;
            }
        }
        /*
        std::cerr << "Got value " << v << ", as u8: " << ((int) to_u8(v)) << std::endl;
        */
        buffer[i] = to_u8(v);
    }


}

__attribute__((noinline))
void render_sample_track(unsigned int samples, unsigned char *buffer, unsigned char *note_buffer, size_t &sample_size,
                         const Json::Value &track) {
    load_sample(note_buffer, &sample_size, DATA_DIR /
                ((track["type"] == "SAMPLE_PRESET") ? SAMPLE_DIR : std::filesystem::path(USERNAME) / SAMPLE_DIR),
                track["id"].asString());
    adjust_volume(note_buffer, sample_size, track["vol"].asDouble());
    for (auto &&beat: track["notes"]) {
        size_t offset = lround(60.0 * beat.asDouble() * SAMPLE_RATE / SONG_INFO.bpm);
        audio_add(buffer, samples, offset, note_buffer, sample_size);
    }
}

__attribute__((noinline))
void render_synth_track(unsigned int samples, unsigned char *buffer, unsigned char *note_buffer, size_t &sample_size,
                        const Json::Value &track) {
    auto synth_stack = load_synth(DATA_DIR /
            ((track["type"] == "SYNTH_PRESET") ? SYNTH_DIR : std::filesystem::path(USERNAME) / SYNTH_DIR),
            track["id"].asString());
    auto env = track["env"];
    size_t a = env["a"].asInt();
    size_t d = env["d"].asInt();
    double s = env["s"].asDouble();
    size_t r = env["r"].asInt();
    double v = track["vol"].asDouble();
    for (auto &&note: track["notes"]) {
        render_note(note_buffer, &sample_size, note, synth_stack);
        adsr(note_buffer, sample_size, a, d, s, r);
        adjust_volume(note_buffer, sample_size, v);
        auto beat = note["t"];
        size_t offset = lround(60.0 * beat.asDouble() * SAMPLE_RATE / SONG_INFO.bpm);
        audio_add(buffer, samples, offset, note_buffer, sample_size);
    }
}

__attribute__((noinline))
void render_tracks(Json::Value tracks, unsigned int samples, unsigned char *buffer) {

    for (
        auto &&track: tracks) {
        memset(NOTE_BUFFER,
               0x80, MAX_SAMPLE_SIZE);
        if (track["type"] == "SAMPLE_PRESET" || track["type"] == "SAMPLE_USER") {
            render_sample_track(samples, buffer, NOTE_BUFFER, NOTE_BUFFER_LEN, track);
        } else if (track["type"] == "SYNTH_PRESET" || track["type"] == "SYNTH_USER") {
            render_synth_track(samples, buffer, NOTE_BUFFER, NOTE_BUFFER_LEN, track);
        } else {
            std::cerr << "Unknown track type " << track["type"] << "!" << std::endl;
        }

    }
}


int main(int argc, char **argv) {
    if (argc < 2 || !filename_is_valid(argv[1])) {
        std::cerr << "Usage: " << argv[0] << " <username>" << std::endl;
        return -1;
    }

    strcpy(USERNAME, argv[1]);

    Json::Value song_info;
    std::cin >> song_info;

    SONG_INFO.bpm = song_info["bpm"].asDouble();
    unsigned int length = song_info["length"].asInt();
    unsigned int n_tracks = song_info["tracks"].size();

    unsigned int total_samples = lround(60.0 * length * SAMPLE_RATE / SONG_INFO.bpm);

    /*
    std::cerr << "Song Info:\n BPM: " << SONG_INFO.bpm << "\n Length: " << length << " beats (" << total_samples
              << " samples)\n Tracks: " << n_tracks << std::endl;
    */
    auto *song_buffer = new unsigned char[total_samples];
    std::fill_n(song_buffer, total_samples, 0x80);

    render_tracks(song_info["tracks"], total_samples, song_buffer);

    SF_INFO sfinfo{
            .frames = total_samples,
            .samplerate = SAMPLE_RATE,
            .channels = 1,
            .format = (SF_FORMAT_WAV | SF_FORMAT_PCM_U8),

    };
    auto output_file = sf_open_fd(stdout->_fileno, SFM_WRITE, &sfinfo,
                                  false);//sf_open("./output.wav", SFM_WRITE, &sfinfo);
    sf_write_raw(output_file, song_buffer, total_samples);
    sf_close(output_file);

    return 0;
}
