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
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

#### Google Cloud Platform Deployment Dependencies
- If deploying via Google Cloud
```bash
brew cask install google-cloud-sdk
gcloud init
# TODO add project-specific configuration instructions
```

### 🐍 Python Environment

- Snake menagerie tamed via [pyenv](https://github.com/pyenv/) and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)
- Install Python 2 if necessary
```bash
pyenv install 2.7.13
```
- Create new virtual environment
```bash
pyenv virtualenv 2.7.13 pymoji
echo 'pymoji' > .python-version
```
- Install dependencies
```bash
pip install -r requirements.txt
```


## Run Local

```bash
python main.py
```

Open a browser and navigate to:
```bash
http://localhost:8080
```


## Deploy to Cloud (Manual)

```bash
gcloud app deploy
gcloud app browse
```


