import argparse

import d3rlpy


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--game", type=str, default="breakout")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--gpu", type=int)
    parser.add_argument("--compile", action="store_true")
    args = parser.parse_args()

    # fix seed
    d3rlpy.seed(args.seed)

    dataset, env = d3rlpy.datasets.get_atari_transitions(
        args.game,
        fraction=0.01,
        index=1 if args.game == "asterix" else 0,
        num_stack=4,
    )

    d3rlpy.envs.seed_env(env, args.seed)

    dqn = d3rlpy.algos.DQNConfig(
        learning_rate=5e-5,
        optim_factory=d3rlpy.optimizers.AdamFactory(eps=1e-2 / 32),
        batch_size=32,
        q_func_factory=d3rlpy.models.q_functions.QRQFunctionFactory(
            n_quantiles=200
        ),
        observation_scaler=d3rlpy.preprocessing.PixelObservationScaler(),
        target_update_interval=2000,
        reward_scaler=d3rlpy.preprocessing.ClipRewardScaler(-1.0, 1.0),
        compile_graph=args.compile,
    ).create(device=args.gpu)

    env_scorer = d3rlpy.metrics.EnvironmentEvaluator(env, epsilon=0.001)

    dqn.fit(
        dataset,
        n_steps=50000000 // 4,
        n_steps_per_epoch=125000,
        save_interval=10,
        evaluators={"environment": env_scorer},
        experiment_name=f"QRDQN_{args.game}_{args.seed}",
    )


if __name__ == "__main__":
    main()
