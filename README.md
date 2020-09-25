# MARS: Mass Reduction Software

## Dependencies:
 - Python 3.7.3:  
    https://www.python.org/downloads/release/python-373/

 - Kivy v1.11.1:
    ```
    python -m pip install kivy==1.11.1
    python -m pip install kivy-garden
    garden install matplotlib
    ```
 - numpy: 1.17.2:
    ```
    python -m pip install numpy==1.17.2
    ```

 - scipy.stats 1.3.1:
    ```
    python -m pip install scipy==1.3.1
    ```

 - Python 3.7.3 statistics  
 
 - Python 3.7.3 math


## Runinng MARS:
There are two options for running an input file - through the user interface or directly through the command line. Output files are written out to the current working directory.
 - #### Command line:
    ```
    python RunFile.py 12345-config.txt
    ```
    Output file will be saved as 12345-out.txt

 - #### User Interface:
    Lauch UI:
    ```
    python FrontEnd.py &
    ```

    Build input file with the input buttons and run with the Run button.

- #### Running Tests:
    Tests are run automatically on startup of the frontend. Tests can also be run through the front end, clicking on Run Tests in the top menu.  
    Tests can manually be run by starting the test suite directly:
    ```
    python TestSuite.py
    ```