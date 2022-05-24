import os
import sys
import glob
import re
from typing import List

import saarsecVV.gamelib.flag_ids as flag_ids


def get_flag_id_config(directory) -> List[str]:
	for fname in glob.glob(directory + '/*.py'):
		with open(fname, 'r') as f:
			matches = re.findall(r'flag_id_types\s*=\s*(\[[^\]]*\])', f.read())
			if len(matches) > 0:
				return eval(matches[0])
	return []


def get_flag_ids(config: List[str], ticks) -> List[List[str]]:
	result = []
	for tick in ticks:
		result.append([flag_ids.generate_flag_id(t, 1, 1, tick, i) for i, t in enumerate(config)])
	return result


def main():
	base = os.path.dirname(os.path.abspath(__file__))
	for d in sorted(glob.glob(base + '/*/checkers')):
		name = os.path.basename(os.path.dirname(d))
		print(f'=== SERVICE {name} ===')
		flag_id_types = get_flag_id_config(d)
		if flag_id_types:
			flag_ids = get_flag_ids(flag_id_types, range(1, 4))
			for i, ids in zip(range(1, 4), flag_ids):
				print(f'- tick {i}: {ids}')
		else:
			print('(no flag ids)')
		if name == 'backd00r':
			print('(not all flags have flag ids)')
		print('\n')


if __name__ == '__main__':
	main()
