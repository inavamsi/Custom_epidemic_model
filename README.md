# Custom compartment model

Use can construct a custom agent based epidemic compartment model. The default model is an SIR model but can be easily changed by changing the number of compartments and transitions.

This repo was built using the Episimmer codebase : https://github.com/corollary-health/episimmer

Test out the UI at : https://share.streamlit.io/inavamsi/custom_epidemic_model/main/Main.py

## Run
To run locally

    cd YACHT
    streamlit run Main.py

This opens up a UI that is fairly simple to navigate and build a custom model. Some standard models include SIR, SEIR, SEYAR, SIRD, MSIRS, ... to name a few.
