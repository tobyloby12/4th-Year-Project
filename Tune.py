""" Optuna example that optimizes the hyperparameters of
a reinforcement learning agent using A2C implementation from Stable-Baselines3
on a OpenAI Gym environment.
This is a simplified version of what can be found in https://github.com/DLR-RM/rl-baselines3-zoo.
You can run this example as follows:
    $ python train.py
"""
from typing import Any
from typing import Dict

import gym
import optuna
from optuna.pruners import MedianPruner
from optuna.samplers import TPESampler
from stable_baselines3 import DQN
from stable_baselines3.common.callbacks import EvalCallback
import torch
import torch.nn as nn
from optical_network_game.node import *
from optical_network_game.link import *
from optical_network_game.requests import *
from optical_network_game.user import *
import pygame, sys
from pygame.locals import *
from gym import spaces
from stable_baselines3.common.env_checker import check_env

#additional code added by me just for testing
import matplotlib
import matplotlib.pyplot as plt
#importing IPython's display module to plot images
is_ipython = 'inline' in matplotlib.get_backend()
if is_ipython: from IPython import display
from itertools import count
import time
from IPython.display import clear_output

#Importing game_gym class for use
import importlib
import optical_network_game.game_gym
importlib.reload(optical_network_game.game_gym)
from optical_network_game.game_gym import *


#TUNING PARAMETERS 
#You can change these to edit the tuning process
N_TRIALS = 100
N_STARTUP_TRIALS = 5
N_EVALUATIONS = 3
N_TIMESTEPS = int(100000)
EVAL_FREQ = int(N_TIMESTEPS / N_EVALUATIONS)
N_EVAL_EPISODES = 3

#ENV_ID = "CartPole-v1"

# Create and wrap the environment
nodeList, linkList = createTestTopology()
#changed to only have 1 request per episode
#from 6 originally
requestList = generateRequests(nodeList, 6)
user = User()

#DEFAULT MODEL PARAMETERS
#Change cuda to auto if you are not using a computer with CUDA Enabled GPU
DEFAULT_HYPERPARAMS = {
    "policy": "MlpPolicy",
    "buffer_size": 500,
    #"eps_fraction": 0.8,
    "exploration_final_eps": 0.05,
    "train_freq": (1000, "step"),
    "target_update_interval": 10000,
    #"env": ENV_ID,
    "device": "cpu",
}


def sample_dqn_params(trial: optuna.Trial) -> Dict[str, Any]:
    """
    Sampler for DQN hyperparams.
    :param trial:
    :return:
    """
    gamma = trial.suggest_categorical("gamma", [0.9, 0.95, 0.98, 0.99, 0.995, 0.999, 0.9999])
    learning_rate = trial.suggest_loguniform("learning_rate", 1e-5, 1)
    #batch_size = trial.suggest_categorical("batch_size", [16, 32, 64, 100, 128, 256, 512])
    #buffer_size = trial.suggest_categorical("buffer_size", [int(1e4), int(5e4), int(1e5), int(1e6)])
    #exploration_final_eps = trial.suggest_uniform("exploration_final_eps", 0, 0.2)
    exploration_fraction = trial.suggest_uniform("exploration_fraction", 0, 0.5)
    target_update_interval = trial.suggest_categorical("target_update_interval", [10000, 15000, 20000])
    learning_starts = trial.suggest_categorical("learning_starts", [0, 1000, 5000, 10000, 20000])

    #train_freq = trial.suggest_categorical("train_freq", [1, 4, 8, 16, 128, 256, 1000])
    #subsample_steps = trial.suggest_categorical("subsample_steps", [1, 2, 4, 8])
    #gradient_steps = max(train_freq // subsample_steps, 1)

    #net_arch = trial.suggest_categorical("net_arch", ["tiny", "small", "medium"])

    #net_arch = {"tiny": [64], "small": [64, 64], "medium": [256, 256]}[net_arch]

    hyperparams = {
        "gamma": gamma,
        "learning_rate": learning_rate,
        #"batch_size": batch_size,
        #"buffer_size": buffer_size,
        #"train_freq": train_freq,
        #"gradient_steps": gradient_steps,
        "exploration_fraction": exploration_fraction,
        #"exploration_final_eps": exploration_final_eps,
        "target_update_interval": target_update_interval,
        "learning_starts": learning_starts,
        #"policy_kwargs": dict(net_arch=net_arch),
    }

    #if trial.using_her_replay_buffer:
    #    hyperparams = sample_her_params(trial, hyperparams)

    return hyperparams


class TrialEvalCallback(EvalCallback):
    """Callback used for evaluating and reporting a trial."""

    def __init__(
        self,
        eval_env: gym.Env,
        trial: optuna.Trial,
        n_eval_episodes: int = 5,
        eval_freq: int = 10000,
        deterministic: bool = True,
        verbose: int = 0,
    ):

        super().__init__(
            eval_env=eval_env,
            n_eval_episodes=n_eval_episodes,
            eval_freq=eval_freq,
            deterministic=deterministic,
            verbose=verbose,
        )
        self.trial = trial
        self.eval_idx = 0
        self.is_pruned = False

    def _on_step(self) -> bool:
        if self.eval_freq > 0 and self.n_calls % self.eval_freq == 0:
            super()._on_step()
            self.eval_idx += 1
            self.trial.report(self.last_mean_reward, self.eval_idx)
            # Prune trial if need
            if self.trial.should_prune():
                self.is_pruned = True
                return False
        return True


def objective(trial: optuna.Trial) -> float:

    kwargs = DEFAULT_HYPERPARAMS.copy()
    # Sample hyperparameters
    kwargs.update(sample_dqn_params(trial))
    # Create the RL model
    enveon = game_gym(nodeList, linkList, requestList, user)
    check_env(enveon)

    model = DQN(**kwargs, env=enveon)
    # Create env used for evaluation
    #INSERT GAME_GYM EON ENV
    eval_env = game_gym(nodeList, linkList, requestList, user)
    check_env(eval_env)

    # Create the callback that will periodically evaluate
    # and report the performance
    eval_callback = TrialEvalCallback(
        eval_env, trial, n_eval_episodes=N_EVAL_EPISODES, eval_freq=EVAL_FREQ, deterministic=True
    )

    nan_encountered = False
    try:
        model.learn(N_TIMESTEPS, callback=eval_callback)
    except AssertionError as e:
        # Sometimes, random hyperparams can generate NaN
        print(e)
        nan_encountered = True
    finally:
        # Free memory
        model.env.close()
        eval_env.close()

    # Tell the optimizer that the trial failed
    if nan_encountered:
        return float("nan")

    if eval_callback.is_pruned:
        raise optuna.exceptions.TrialPruned()

    return eval_callback.last_mean_reward


if __name__ == "__main__":
    # Set pytorch num threads to 1 for faster training
    torch.set_num_threads(1)

    sampler = TPESampler(n_startup_trials=N_STARTUP_TRIALS)
    # Do not prune before 1/3 of the max budget is used
    pruner = MedianPruner(n_startup_trials=N_STARTUP_TRIALS, n_warmup_steps=N_EVALUATIONS // 3)

    study = optuna.create_study(sampler=sampler, pruner=pruner, direction="maximize")
    try:
        study.optimize(objective, n_trials=N_TRIALS, timeout=600)
    except KeyboardInterrupt:
        pass

    print("Number of finished trials: ", len(study.trials))

    print("Best trial:")
    trial = study.best_trial

    print("  Value: ", trial.value)

    print("  Params: ")
    for key, value in trial.params.items():
        print("    {}: {}".format(key, value))

    print("  User attrs:")
    for key, value in trial.user_attrs.items():
        print("    {}: {}".format(key, value))