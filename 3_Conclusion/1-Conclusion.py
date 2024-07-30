import streamlit as st

st.header("Conclusion")
'''
This project simulated, visualized and analyzed a solar hot water panel and storage tank system. Key insights from that analysis were:
- Without pump control, the tank temperature would drop to near outdoor air temp every night.
- With a basic pump control sequence, tank temperature will rise day-to-day, if outdoor air temperatures isn't too cold. Heat loss to the surrounding environment was the dominant factor in winter. 
- An unoptimized random forest model captured 99% of the variance and predicted tank temperatures with an average error of 0.17°C.

'''
st.subheader("Future Work")
'''
- Optimize the pump control to find the max flow rate that maximizes tank temperature and minimizes pump runtime. 
- Add explicit radiation losses instead of constant heat transfer coefficients.
- Add more complex geometry to the solar panel.
- Incorporate additional physical properties about the pump.
'''