# MUSIC
Creation of an application to extract Material from Sequences of Interpretations of musical Compositions
- .py file : python implementation of the application with a GUI. In order to build the application with pyInstaller: 
   - place in a folder 
   - run `pyinstaller MUSIC_experiments.py --onefile`
   - Open your .spec file
   - At the top of the file, under the `block_cipher = None`, add the following function:
    ```
    def get_mediapipe_path():
        import mediapipe
        mediapipe_path = mediapipe.__path__[0]
        return mediapipe_path
    ```
   - Then, after the following lines:
    ```
    pyz = PYZ(a.pure, a.zipped_data,
                 cipher=block_cipher)
    ```
    add the following lines which utilize the native Tree class to create a TOC for the binary:
    ```
    mediapipe_tree = Tree(get_mediapipe_path(), prefix='mediapipe', excludes=["*.pyc"])
    a.datas += mediapipe_tree
    a.binaries = filter(lambda x: 'mediapipe' not in x[0], a.binaries)
    ```
   - `pyinstaller --debug=all MUSIC_experiments.spec --windowed --onefile`

(solution from https://stackoverflow.com/questions/67887088/issues-compiling-mediapipe-with-pyinstaller-on-macos)
