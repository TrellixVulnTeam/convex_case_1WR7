import itertools
import numpy as np
import subprocess
import time
import sys
import os
import pandas as pd


def run_experiment(dp_notion='example_level', max_grad_norm=10.0, noise_multiplier=0.51,
	meta_batch=5, meta_iters=20000, meta_step=0.1, meta_step_final=0.0,
	classes=5, shots=1, train_shots=10,
	inner_batch=10, inner_iters=5, learning_rate=1e-3,
	eval_batch=5, eval_iters=50, eval_samples=1000, eval_interval=5000,
	seeds=[0], transductive=True, sgd=False, dp_sgd_lr=1e-3):

	print('Calling commands...')
	processes = [None for _ in range(len(seeds))]

	# CHANGE THIS LATER
	result_dir = './results/mini_imagenet/hyper_search/5_shot_5_way/example_level/meta_batches_{0:.1f}_meta_iters_{1:.1f}_inner_batch{2:.2f}_grad_{3:.5f}_noise_multiplier_{4:.4f}_meta_step_{5:.4f}_meta_step_final_{6:.4f}_learning_rate_{7:.4f}_dp_sgd_lr_{8:.4f}_train_shots{9:.2f}'.format(
		meta_batch, meta_iters, inner_batch, max_grad_norm, noise_multiplier, meta_step, meta_step_final, learning_rate, dp_sgd_lr, train_shots)

	#seen_seed = None
	#if seen_seed:
	#	csv_file = metrics_dir + "/seed_" + str(seen_seed) + ".csv"
	#	print(csv_file)
	#	if os.path.exists(csv_file):
	#		csv_results = load_data(csv_file)
	#		max_acc = get_accuracy_vs_round_number(csv_results)[1].max()
	#	else:
	#		max_acc = 1.0
	#else:
	#	max_acc = 1.0

	max_acc = 1.0
	if max_acc > 0.09:
		for i, seed in enumerate(seeds):
			result_file = 'seed_{}'.format(seed)
			commands = ['python3', 'run_miniimagenet_example_level.py']		# Change this depending on dataset
			commands.extend(
				['--dp-notion', str(dp_notion),
				'--max-grad-norm', str(max_grad_norm),
				'--noise-multiplier', str(noise_multiplier),
				'--meta-batch', str(meta_batch),
				'--meta-iters', str(meta_iters),
				'--meta-step', str(meta_step),
				'--meta-step-final', str(meta_step_final),
				'--classes', str(classes),
				'--shots', str(shots),
				'--train-shots', str(train_shots),
				'--inner-batch', str(inner_batch),
				'--inner-iters', str(inner_iters),
				'--learning-rate', str(learning_rate),
				'--eval-batch', str(eval_batch),
				'--eval-iters', str(eval_iters),
				'--eval-samples', str(eval_samples),
				'--eval-interval', str(eval_interval),
				'--seed', str(seed),
				'--result-dir', str(result_dir),
				'--result-file', str(result_file),
				'--dp-sgd-lr', str(dp_sgd_lr) ])

			if transductive:
				commands.extend(['--transductive'])
			if sgd:
				comands.extend(['--sgd'])

			process = subprocess.Popen(commands)
			processes[i] = process
			print('process {} initiated'.format(i))

		done = 0
		while done < len(seeds):
			time.sleep(60)
			for i, process in enumerate(processes):
				status = process.poll()
				if status == None:
					continue
				elif status == 0:
					done += 1
					print('process {} done!!!'.format(i))
				else:
					print('process {} failed with status: {}'.format(i, status))
					print('some process failed! debug!')
					return

	print('Done!!!')


search = "initial_tuning"
if len(sys.argv) > 1:
	seeds = [int(sys.argv[1])]
else:
	seeds = [8164600]

if search == "initial_tuning":

	# Privacy Params
	max_grad_norm = [0.7]		# Change this
	noise_multiplier = 0.564
	dp_sgd_lr = [5e-4]			# Change this

	# Problem Setup
	classes = 5
	shots = 5
	train_shots = [45]			# Change this

	# Outer Optimization
	meta_batch = [50]			# Change this
	meta_step = [1.0]
	meta_step_final = 0.0
	meta_iters = int(10000 / meta_batch[0])


	# Inner Optimization
	inner_batch = [30]			# Change this one
	inner_iters = 8				# Change this
	learning_rate = [1e-3]

	# Eval Parameters
	eval_iters = 50
	eval_batch = 15
	eval_samples = 1000
	eval_interval = int(100000 / meta_batch[0] / 10)

	choices = 2


experiments = list(itertools.product(max_grad_norm, meta_batch, inner_batch, meta_step, learning_rate, dp_sgd_lr, train_shots))
np.random.seed(234)
perm = np.random.choice(len(experiments), choices, replace=False)

for i in perm:
	max_grad_norm, meta_batch, inner_batch, meta_step, learning_rate, dp_sgd_lr, train_shots = experiments[i]

	run_experiment(
		dp_notion='example_level',
		max_grad_norm=max_grad_norm,
		noise_multiplier=noise_multiplier,
		dp_sgd_lr=dp_sgd_lr,
		meta_batch=meta_batch,
		meta_iters=meta_iters,
		meta_step=meta_step,
		meta_step_final=0.0,
		classes=classes,
		shots=shots,
		train_shots=train_shots,
		inner_batch=inner_batch,
		inner_iters=inner_iters,
		learning_rate=learning_rate,
		eval_iters=eval_iters,
		eval_batch=eval_batch,
		eval_samples=eval_samples,
		eval_interval=eval_interval,
		seeds=seeds,
		transductive=True,
		sgd=False)

print('Done with experiments!')
