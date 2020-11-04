from setuptools import setup

setup(name='gym_air_hockey',
      version='1.0.0',
      description='OpenAI Gym Environment Wrapper for Air Hockey Game Simulator',
      author=['Akhmed Rakhmati', 'me'],
      install_requires=['gym',
                        'pygame',
                        'numpy',
                        'opencv-python']
)