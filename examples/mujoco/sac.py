import os
import datetime
import argparse
import gym
import torch.multiprocessing as mp

from rltorch.agent import SacActor, SacLearner

mp.set_start_method('spawn', force=True)


def actor_process(env_id, log_dir, shared_memory, shared_wights,
                  actor_id, cuda=True, seed=0):

    actor = SacActor(
        gym.make(env_id), log_dir, shared_memory, shared_wights,
        actor_id, cuda=cuda, seed=seed)
    actor.run()


def learner_process(env_id, log_dir, shared_memory, shared_wights,
                    cuda=True, seed=0):

    actor = SacLearner(
        gym.make(env_id), log_dir, shared_memory, shared_wights,
        cuda=cuda, seed=seed)
    actor.run()


def run():
    mp.freeze_support()

    parser = argparse.ArgumentParser()
    parser.add_argument('--env_id', type=str, default='HalfCheetah-v2')
    parser.add_argument('-n', '--num_actors', type=int, default=1)
    parser.add_argument('--cuda', action='store_true')
    parser.add_argument('--seed', type=int, default=0)
    args = parser.parse_args()

    log_dir = os.path.join(
        'logs', args.env_id,
        f'sac-{datetime.datetime.now().strftime("%Y%m%d-%H%M")}')

    shared_memory = mp.Queue(100)
    mp_manager = mp.Manager()
    shared_wights = mp_manager.dict()

    learner_args = (
        args.env_id, log_dir, shared_memory, shared_wights, args.cuda,
        args.seed)
    processes = [mp.Process(target=learner_process, args=learner_args)]

    for actor_id in range(args.num_actors):
        actor_args = (
            args.env_id, log_dir, shared_memory, shared_wights, actor_id,
            args.cuda, args.seed,)
        processes.append(
            mp.Process(target=actor_process, args=actor_args))

    for pi in range(len(processes)):
        processes[pi].start()

    for p in processes:
        p.join()


if __name__ == '__main__':
    run()