# pymoji


## Install

### 🍺 OS Dependencies

- Install and update [Homebrew](https://brew.sh/) if necessary
```bash
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew update
brew doctor
```
- Install dependencies
```bash
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
```bash
brew cask install google-cloud-sdk
gcloud init
# enter 'pymoji-176318' for project
```

### 🐍 Python Environment

- Snake menagerie tamed via [pyenv](https://github.com/pyenv/) and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)
- Install Python 3 if necessary
```bash
pyenv install 3.5.3
```
- Create new virtual environment
```bash
pyenv virtualenv 3.5.3 pymoji
```
- Install dependencies
```bash
cd pymoji
echo 'pymoji' > .python-version
pip install -r requirements.txt
```

### Git Hooks

- Auomatically run linters before pushing:
```bash
cd pymoji
./git-pre-push.sh
```

### Sublime
- http://mathalope.co.uk/2017/05/19/sublime-text-3-how-to-set-different-tab-size-based-on-file-type/
- Optional: [SublimeLinter](http://sublimelinter.readthedocs.io/en/latest/)
  - [pylint extension](https://packagecontrol.io/packages/SublimeLinter-pylint)
  - [eslint extension](https://packagecontrol.io/packages/SublimeLinter-contrib-eslint)
  - IMPORTANT: because reasons, you must also do some global setup:
  ```bash
  pyenv global 3.5.3
  cd ~ # go somewhere that falls through to global environment
  pip install pylint
  ```


## Run Local

- Open a terminal and run the dev server:
```bash
cd pymoji
python manage.py runserver
```

- Open a browser and navigate to http://localhost:5000


## Deploy to Cloud (Manual)

```bash
gcloud app deploy --project pymoji-176318
```


