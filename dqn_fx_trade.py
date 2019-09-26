import fx_trade
import numpy as np
import gym

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, LSTM, Reshape
from keras.optimizers import Adam

from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory


ENV_NAME_TRAIN = 'fx_trade_train-v0'
ENV_NAME_TEST = 'fx_trade_test-v0'



# Get the environment and extract the number of actions.
env_train = gym.make(ENV_NAME_TRAIN)
np.random.seed(123)
env_train.seed(123)
nb_actions = env_train.action_space.n

lstm = True
#lstm = False


if lstm == True:
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + env_train.observation_space.shape))
    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Reshape((16, 1), input_shape=(16, )))
    model.add(LSTM(50, input_shape=(16, 1), 
              return_sequences=False,
              dropout=0.0))
    model.add(Dense(nb_actions))
    model.add(Activation('sigmoid'))
    print(model.summary())

else:
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + env_train.observation_space.shape))
    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Dense(nb_actions))
    model.add(Activation('sigmoid'))
    print(model.summary())


# Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
# even the metrics!
memory = SequentialMemory(limit=100, window_length=1)
policy = BoltzmannQPolicy()
#policy = EpsGreedyQPolicy(eps=0.1)
dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=10,
               target_model_update=1e-2, policy=policy)
dqn.compile(Adam(lr=1e-3), metrics=['mae'])

# Okay, now it's time to learn something! We visualize the training here for show, but this
# slows down training quite a lot. You can always safely abort the training prematurely using
# Ctrl + C.
dqn.fit(env_train, nb_steps=20000, visualize=True, verbose=2)

# After training is done, we save the final weights.

dqn.save_weights('dqn_{}_weights.h5f'.format(ENV_NAME_TRAIN), overwrite=True)

# Finally, evaluate our algorithm for 5 episodes.
env_test = gym.make(ENV_NAME_TEST)
np.random.seed(123)
env_test.seed(123)
dqn.test(env_test, nb_episodes=1, visualize=True)
