# ✨📸🕶 Emojivision 🕶📸✨
Basic Flask web application that uses the Google Vision API to replace faces with emoji.
- http://tensorbros.com
- https://circleci.com/gh/TensorBros/pymoji
- https://console.cloud.google.com/home/dashboard?project=pymoji-176318
- https://app.google.stackdriver.com/?project=pymoji-176318


## 🛠 Install

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

#### ☁ Google Cloud Platform Deployment Dependencies
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
pyenv install 3.6.2 # necessary for pymoji
```
- Create new virtual environment
```
pyenv virtualenv 3.6.2 pymoji
```
- Install dependencies
```
cd <project-dir>
echo 'pymoji' > .python-version
pip install --upgrade pip setuptools
pip install -r requirements.txt
```

#### ☁ Google Vision Dependency
- If you're running locally, Google Vision API calls require the user to have [
Google Application Default Credentials](https://cloud.google.com/sdk/gcloud/reference/auth/application-default/login).

If you haven't yet, you'll need to install google-cloud-sdk.
You may also need to manually and temporarily change your global python version to `pyenv global 2.7.13`. Make sure `.python-version` is correctly set to `pymoji`.

```
# This will open a browser for you to Oauth
gcloud auth application-default login
```
Note that this is basically [step #2 in this list](https://developers.google.com/identity/protocols/application-default-credentials); automated robots need to use step #1.


### 🎣 Git Hooks

- Auomatically run linters before pushing:
```
cd <project-dir>
./git-pre-push.sh
```

### 📝 Sublime
- http://mathalope.co.uk/2017/05/19/sublime-text-3-how-to-set-different-tab-size-based-on-file-type/
- Optional: [SublimeLinter](http://sublimelinter.readthedocs.io/en/latest/)
  - [pylint extension](https://packagecontrol.io/packages/SublimeLinter-pylint)
  - [eslint extension](https://packagecontrol.io/packages/SublimeLinter-contrib-eslint)
  - IMPORTANT: because reasons, you must also do some global setup:
  ```
  pyenv global 3.6.2
  cd ~ # go somewhere that falls through to global environment
  pip install pylint pylint-flask
  ```


## 💻 Local Environment

### ⚙ Initial Configuration
- Start by cloning a new developer config
```
cd <project-dir>
cp config.py instance/local_config.py
```

- Edit `instance/local_config.py` as needed. Be sure to set `SERVER_NAME=None`!
```python
# probably good to at least set these:
DEBUG = True
TESTING = True # also controls local VS google cloud services
# IMPORTANT: when running local dev environment, must override and set to None
SERVER_NAME = None

# optional overrides
MAX_RESULTS = 5
# ...
```

- Make sure everything works
```
cd <project-dir>
./cli build
```

### 🌎 Localhost Webserver

- Open a terminal and run the dev webserver:
```
cd <project-dir>
./cli runserver
```

- Open a browser and navigate to http://localhost:5000


### ⌨ Command Line Interface

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


### ☁ Deploy to Cloud (Manual)

```
cd <project-dir>
./gc app deploy --project pymoji-176318 --promote --stop-previous-version
```


