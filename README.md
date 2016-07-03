# RepoHub
Automatic monitoring of local repositories (svn,git)


## Install

The software requires the following python libraries and software (for Python 3):

* tornado (python 3)
* subversion (svn command line)

under ubuntu you need only install the following: 
```
sudo apt-get install python3-tornado
```

## Config

RepoHub uses local confug file located at ~/.config/repohub.

The files ```config.ini``` and ```repos.ini``` contain respectively the global parameters of the app and the repository list.
