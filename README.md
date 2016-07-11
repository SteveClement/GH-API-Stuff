# Some fun with api.github.com

## emoji

Pulls the emojis from the API (puts it into an sqlite DB) and displays them in browser.

### Installation

```
git clone https://github.com/SteveClement/GH-API-Stuff.git
cd GH-API-Stuff/emoji
pip3 install -r requirements
python3 emoji.py
```

#### FreeBSD

On FreeBSD you need to install the py35-sqlite3 package

```
# portinstall py35-sqlite3
```
