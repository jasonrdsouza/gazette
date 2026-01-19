## Gazette
Personal newspaper service

### Developing

Dev console
```
uv run ipython
```

Format python files
```
uv run black gazette/
```

Analyze a new feed
```
uv run python -m gazette.editor <RSS_URL>
```
