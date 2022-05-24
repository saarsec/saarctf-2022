import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import wave

from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Exists, OuterRef
from django.http import HttpResponseForbidden, FileResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

from app.models import Loop, Vote
from saarloop.settings import DATADIR, BASE_DIR, MAX_SAMPLE_SIZE, SAMPLE_RATE


def index(request):
    loops = Loop.objects.filter(public=True).annotate(votes=Count('vote')).order_by('-votes', '-id')[:16]
    if request.user.is_authenticated:
        loops = loops.annotate(has_voted=Exists(Vote.objects.filter(loop_id=OuterRef('id'), user=request.user)))
    return render(request, "index.html", {'loops': loops})


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, "Successfully logged in")
            return redirect(reverse('index'))
        messages.warning(request, "Log-in failed")
    return render(request, "login.html")


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        if None in (username, password):
            messages.warning(request, "Please provide username and password")
        else:
            user = User.objects.create_user(username=username, password=password)
            if user is not None:
                user.save()
                auth.login(request, user)
                messages.success(request, f"Registered new user {user}")
                return redirect(reverse('index'))
        messages.warning(request, "Registration failed")
    return render(request, "register.html")


def logout(request):
    auth.logout(request)
    messages.success(request, 'Successfully logged out')
    return redirect(reverse('index'))


def download(request, loop_id):
    loop = get_object_or_404(Loop, pk=loop_id)
    if not loop.public and request.user != loop.artist:
        return HttpResponseForbidden()
    return FileResponse(open(DATADIR / "loops" / f"{loop.id}_{loop.name}.wav", "rb"), filename=f"{loop.name}.wav")


@login_required
def loops(request):
    loops = Loop.objects.filter(artist=request.user).annotate(votes=Count('vote')).order_by("-pk")
    synths = sorted(
        ("PRESET", os.path.splitext(os.path.basename(p))[0]) for p in (DATADIR / "synths").glob("*.json")) + sorted(
        ("USER", os.path.splitext(os.path.basename(p))[0]) for p in
        (DATADIR / request.user.username / "synths").glob("*.json"))
    samples = sorted(
        ("PRESET", os.path.splitext(os.path.basename(p))[0]) for p in (DATADIR / "samples").glob("*.wav")) + sorted(
        ("USER", os.path.splitext(os.path.basename(p))[0]) for p in
        (DATADIR / request.user.username / "samples").glob("*.wav"))
    return render(request, "loops.html",
                  {"loops": loops, "synths": synths, "samples": samples})


@login_required
def samples(request):
    samples = sorted(
        os.path.splitext(os.path.basename(p))[0] for p in (DATADIR / request.user.username / "samples").glob("*.wav"))
    return render(request, "samples.html", {'samples': samples})


@login_required
def synths(request):
    synths = sorted(
        os.path.splitext(os.path.basename(p))[0] for p in (DATADIR / request.user.username / "synths").glob("*.json"))
    return render(request, "synths.html", {'synths': synths})


@login_required
def publish(request, loop_id):
    loop = Loop.objects.get(pk=loop_id)
    if loop and request.user == loop.artist:
        loop.public = True
        loop.save()
    return redirect(reverse('loops'))


@login_required
def like(request, loop_id):
    loop = Loop.objects.get(pk=loop_id)
    if loop:
        if loop.vote_set.filter(user=request.user).exists():
            loop.vote_set.filter(user=request.user).delete()
        else:
            vote = Vote.objects.create(loop=loop, user=request.user)
            vote.save()
    return redirect(reverse('index'))


@login_required
@require_POST
def create_loop(request):
    loop_data = json.loads(request.POST["loop"])
    loop_name = re.sub(r"[^0-9a-zA-Z -]", "_", request.POST["loop_name"])

    tmp_out = tempfile.NamedTemporaryFile(delete=False)
    p = subprocess.run([BASE_DIR / "engine/saarloop_engine", request.user.username],
                       input=json.dumps(loop_data).encode(), stdout=tmp_out)
    tmp_out.close()
    if p.returncode == 0:
        loop = Loop.objects.create(name=loop_name, artist=request.user, bpm=int(loop_data["bpm"]),
                                   length=int(loop_data["length"]))
        loop.save()
        loop.refresh_from_db()
        loop_file = DATADIR / "loops" / f"{loop.id}_{loop.name}.wav"
        loop_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(tmp_out.name, loop_file)
        with open(DATADIR / "loops" / f"{loop.id}_{loop.name}.json", "w") as f:
            json.dump(loop_data, f)
        messages.success(request, f"Successfully created new loop {loop_name}")
    else:
        messages.error(request, "Error creating loop")
        os.remove(tmp_out.name)

    return redirect(reverse('loops'))


@login_required
@require_POST
def preview_loop(request):
    loop_data = json.loads(request.POST["loop"])
    loop_name = re.sub(r"[^0-9a-zA-Z -]", "_", request.POST["loop_name"])

    tmp_out = tempfile.NamedTemporaryFile(delete=False)
    p = subprocess.run([BASE_DIR / "engine/saarloop_engine", request.user.username],
                       input=json.dumps(loop_data).encode(), stdout=tmp_out)

    if p.returncode == 0:
        tmp_out.seek(0)
        return FileResponse(tmp_out, filename=f"{loop_name}.wav")

    return HttpResponseBadRequest()


@login_required
def sample(request, sample_type, sample_name):
    sample_type = sample_type.upper()
    sample_name = re.sub(r"[^0-9a-zA-Z-]", "_", sample_name)

    searchdir = DATADIR
    if sample_type == 'USER':
        searchdir /= request.user.username

    sample_file = searchdir / "samples" / f"{sample_name}.wav"

    if sample_file.exists():
        return FileResponse(open(sample_file, "rb"), filename=sample_name)

    return HttpResponseNotFound()


@login_required
@require_POST
def new_sample(request):
    sample_file = request.FILES['sample_file']
    sample_name = re.sub(r"[^0-9a-zA-Z-]", "_", os.path.splitext(sample_file.name)[0])

    target_file = DATADIR / request.user.username / "samples" / f"{sample_name}.wav"

    if target_file.exists():
        messages.error(request, f"Sample {sample_name} already exists")

    elif sample_file.size > MAX_SAMPLE_SIZE:
        messages.error(request, "Sample too large")

    else:
        content = sample_file.read()
        with io.BytesIO(content) as buf, wave.open(buf, "rb") as wave_file:
            if wave_file.getnchannels() != 1 or wave_file.getsampwidth() != 1 or wave_file.getframerate() != SAMPLE_RATE:
                messages.error(request, "Invalid sample format")
            else:
                target_file.parent.mkdir(parents=True, exist_ok=True)
                with open(target_file, "wb") as f:
                    f.write(content)
                messages.success(request, f"Successfully uploaded new sample {sample_name}")

    return redirect(reverse('samples'))


@login_required
def synth(request, synth_type, synth_name):
    synth_type = synth_type.upper()
    synth_name = re.sub(r"[^0-9a-zA-Z-]", "_", synth_name)

    searchdir = DATADIR
    if synth_type == 'USER':
        searchdir /= request.user.username

    synth_preview_file = searchdir / "synths" / f"{synth_name}.wav"
    synth_source_file = searchdir / "synths" / f"{synth_name}.json"

    if not synth_preview_file.exists() and synth_source_file.exists():
        preview_loop_data = {
            'bpm': 135,
            'length': 1,
            'tracks': [
                {'type': f'SYNTH_{synth_type}', 'id': synth_name, 'vol': 0.5,
                 'env': {'a': 128, 'd': 128, 's': 0.5, 'r': 128},
                 'notes': [{'t': 0, 'p': 60, 'd': 1}]}
            ]
        }
        with open(synth_preview_file, 'wb') as f:
            subprocess.run([BASE_DIR / "engine/saarloop_engine", request.user.username],
                           input=json.dumps(preview_loop_data).encode(), stdout=f)

    if synth_preview_file.exists():
        return FileResponse(open(synth_preview_file, "rb"), filename=synth_name)

    return HttpResponseNotFound()


@login_required
@require_POST
def new_synth(request):
    synth_data = json.loads(request.POST["synth"])
    synth_name = re.sub(r"[^0-9a-zA-Z-]", "_", request.POST["synth_name"])

    target_file = DATADIR / request.user.username / "synths" / f"{synth_name}.json"

    if target_file.exists():
        messages.error(request, f"Synth {synth_name} already exists")
    else:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with open(target_file, "w") as f:
            json.dump(synth_data, f)
        messages.success(request, f"Successfully created new synth {synth_name}")

    return redirect(reverse('synths'))
