# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
from typing import Dict, Any
import numpy as np
import itertools
import logging
from argparse import ArgumentParser
from tqdm import tqdm

from benchmarking.nursery.benchmark_multiobjective.run_experiment import run_experiment
from syne_tune.blackbox_repository.simulated_tabular_backend import (
    BlackboxRepositoryBackend,
)
from benchmarking.commons.hpo_main_simulator import get_transfer_learning_evaluations
from benchmarking.nursery.benchmark_automl.baselines import MethodArguments

from syne_tune.backend.simulator_backend.simulator_callback import SimulatorCallback
from syne_tune.experiments import load_experiment
from syne_tune.stopping_criterion import StoppingCriterion
from syne_tune.tuner import Tuner


def parse_args(methods: Dict[str, Any], benchmark_definitions: Dict[str, Any]):
    parser = ArgumentParser()
    parser.add_argument(
        "--experiment_tag",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--num_seeds",
        type=int,
        required=False,
        default=3,
        help="number of seeds to run",
    )
    parser.add_argument(
        "--run_all_seeds",
        type=int,
        default=1,
        help="if 1 run all the seeds [0, ``num_seeds``-1], otherwise run seed ``num_seeds`` only",
    )
    parser.add_argument(
        "--start_seed",
        type=int,
        required=False,
        default=0,
        help="first seed to run (if ``run_all_seed`` == 1)",
    )
    parser.add_argument(
        "--method", type=str, required=False, help="a method to run from baselines.py"
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        required=False,
        help="a benchmark to run from benchmark_definitions.py",
    )
    args, _ = parser.parse_known_args()
    args.run_all_seeds = bool(args.run_all_seeds)
    if args.run_all_seeds:
        seeds = list(range(args.start_seed, args.num_seeds))
    else:
        seeds = [args.num_seeds]
    method_names = [args.method] if args.method is not None else list(methods.keys())
    benchmark_names = (
        [args.benchmark]
        if args.benchmark is not None
        else list(benchmark_definitions.keys())
    )
    return args, method_names, benchmark_names, seeds


def main(methods: Dict[str, Any], benchmark_definitions: Dict[str, Any]):
    args, method_names, benchmark_names, seeds = parse_args(
        methods, benchmark_definitions
    )
    experiment_tag = args.experiment_tag

    logging.getLogger("syne_tune.optimizer.schedulers").setLevel(logging.WARNING)
    logging.getLogger("syne_tune.backend").setLevel(logging.WARNING)
    logging.getLogger("syne_tune.backend.simulator_backend.simulator_backend").setLevel(
        logging.WARNING
    )

    combinations = list(itertools.product(method_names, seeds, benchmark_names))
    print(combinations)

    for method, seed, benchmark_name in tqdm(combinations):

        get_trial_scheduler = methods[method]

        benchmark = benchmark_definitions[benchmark_name]

        run_experiment(get_trial_scheduler, seed, benchmark, experiment_tag)


if __name__ == "__main__":
    from benchmarking.nursery.benchmark_multiobjective.baselines import methods
    from benchmarking.nursery.benchmark_multiobjective.benchmark_definitions import (
        benchmark_definitions,
    )

    main(methods, benchmark_definitions)