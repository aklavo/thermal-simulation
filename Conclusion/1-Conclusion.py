import streamlit as st

st.header("Conclusion")
'''
This project created a simple thermal simulation of a solar hot water panel and storage tank. Inputs and outputs of the simulation were 
visualized in a streamlit app allowing for user-input. The results of the simulation were then analyzed. Key insights from that analysis were:
- Without pump control the tank temperature would drop to near outdoor air every night.
- With a basic sequence, tank temperature could rise day-to-day, give outdoor air temperatures wasn't too cold.
- Heat loss to the surrounding was the dominate factor in winter. 
- An out of the box random forest model was able capture 99% of the variance and predict the tank temperatures with an average error of 0.17°C.
'''
st.subheader("Future Work")
'''
- Further develop the pump class, to model electrical input to the system.
- Add explicit radiation losses instead of constant heat transfer coefficients.
- Add more complex geometry to the solar panel.
- Optimization the pump control to find the max flow rate that maximizes tank temperature and minimizes pump runtime. 
- Explore additional ML models.

'''