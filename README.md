# ✨📸🕶 Emojivision 🕶📸✨
Basic Flask web application that uses the Google Vision API to replace faces with emoji.
- http://tensorbros.com
- https://circleci.com/gh/TensorBros/pymoji
- https://console.cloud.google.com/home/dashboard?project=pymoji-176318
- https://app.google.stackdriver.com/?project=pymoji-176318


## Install

### 🍺 OS Dependencies

- Install and update [Homebrew](https://brew.sh/) if necessary
```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew update
brew doctor
```
- Install dependencies
```
brew install coreutils pyenv pyenv-virtualenv
```
- Add required shims to your bash profile:
```bash
# Python shims
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

#### Google Cloud Platform Deployment Dependencies
- If deploying via Google Cloud
```
brew cask install google-cloud-sdk
cd <project-dir>
./gc init
# enter 'pymoji-176318' for project
```

### 🐍 Python Environment

- Snake menagerie tamed via [pyenv](https://github.com/pyenv/) and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)
- Install versions of Python if necessary
```
pyenv install 2.7.13 # necessary for google cloud sdk
pyenv install 3.5.3 # necessary for pymoji
```
- Create new virtual environment
```
pyenv virtualenv 3.5.3 pymoji
```
- Install dependencies
```
cd <project-dir>
echo 'pymoji' > .python-version
pip install --upgrade pip setuptools
pip install -r requirements.txt
```

### Git Hooks

- Auomatically run linters before pushing:
```
cd <project-dir>
./git-pre-push.sh
```

### Sublime
- http://mathalope.co.uk/2017/05/19/sublime-text-3-how-to-set-different-tab-size-based-on-file-type/
- Optional: [SublimeLinter](http://sublimelinter.readthedocs.io/en/latest/)
  - [pylint extension](https://packagecontrol.io/packages/SublimeLinter-pylint)
  - [eslint extension](https://packagecontrol.io/packages/SublimeLinter-contrib-eslint)
  - IMPORTANT: because reasons, you must also do some global setup:
  ```
  pyenv global 3.5.3
  cd ~ # go somewhere that falls through to global environment
  pip install pylint pylint-flask
  ```


## Local Environment

### Initial Configuration
- Start by cloning a new developer config
```
cd <project-dir>
cp config.py instance/config.py
```

- Edit `instance/config.py` as needed
```python
# probably good to at least set these:
DEBUG = True
TESTING = True
SECRET_KEY = 'a-secret-all-your-own' # change this
#SERVER_NAME = 'tensorbros.com' # comment out for localhost
```

- Make sure everything works
```
cd <project-dir>
./cli build
```

### Localhost Webserver

- Open a terminal and run the dev webserver:
```
cd <project-dir>
./cli runserver
```

- Open a browser and navigate to http://localhost:5000


### Command Line Interface

- HALP.
```
cd <project-dir>
./cli -?
```

- Wat do `runserver`?
```
cd <project-dir>
./cli runserver -?
```

- Emojivision a file:
```
cd <project-dir>
./cli runface pymoji/static/uploads/face-input.jpg
```

- Emojivision a directory:
```
cd <project-dir>
./cli rundir pymoji/static/uploads
```


### Deploy to Cloud (Manual)

```
cd <project-dir>
./gc app deploy --project pymoji-176318 --promote --stop-previous-version
```


