# Ignore this code. 
# Made just for my Practice.

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.header("st.button")
st.write("Hello Taha")

btn = st.button("Click me")

st.write(btn)

if btn:
    st.write("Goodbye")
else: 
    st.write("HELlO!")

st.write("**Hello** *World* :smile:")

columns=["Taha", "Mustafa", "Mehlam"]
df = pd.DataFrame(np.random.randn(200, 3), columns=columns)

st.write(df)

def show_graph() -> None:
    plt.figure(figsize=(8, 5))
    
    for col in columns:
        plt.scatter(df.index, df[col], label=col, s=10)
    
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.title("DataFrame Scatter Plot")
    plt.legend()
    
    st.pyplot(plt)
    
if st.button("Show graph"):
    show_graph()
    
    
st.header("st.slider")
rating = st.slider("Rating", 0, 100, 50)
st.write(rating)

st.subheader("range slider")
low, high = st.slider(
    "Range",
    0, 
    100,
    (30, 80)
)

st.line_chart(df)
st.help(st.line_chart)

st.subheader("st.selectbox")
option = st.selectbox(
    "Select Column", df.columns,
)
st.write(option)
# st.write(df[f"{option}"])

st.write(
    df.loc[
        (df[f"{option}"] >= low) & (df[f"{option}"] <= high),
        f"{option}"
    ]
)

st.image("https://imgs.search.brave.com/Bqn0PlR1glcT4tmXQHE6I73QNycPrXTtE5BR6dj1onY/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9pLnJl/ZGQuaXQvbDQ4Znhz/eGFuczdnMS5qcGVn")

st.subheader("st.multiselect")
subjects = st.multiselect(
    "Select your majors",
    ["Physics", "Mathematics", "Operating Systems"]
)

for sub in subjects:
    st.write(sub)
    
st.subheader("Checkbox")
for name in columns:
    check = st.checkbox(name)
        
show = st.toggle("Show Graph")
if show:
    show_graph()
    
