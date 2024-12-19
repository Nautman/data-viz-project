---
theme: dashboard
title: Playground to test
toc: false
---


<style type="text/css">


.countrydot {
  cursor: pointer;
}

</style>


# Rocket launches 🚀


<!-- Load and transform the data -->

```js
const launches = FileAttachment("data/launches.csv").csv({typed: true});
const pcaQ1 = FileAttachment("data/PCAVOL_A_QC1.csv").csv({typed: true});
const pcaQ2 = FileAttachment("data/PCAVOL_A_QC2.csv").csv({typed: true});
const pcaQ3 = FileAttachment("data/PCAVOL_A_QC3_1.csv").csv({typed: true});
```

<!-- A shared color scale for consistency, sorted by the number of launches -->

```js
const color = Plot.scale({
  color: {
    type: "categorical",
    domain: d3.groupSort(launches, (D) => -D.length, (d) => d.state).filter((d) => d !== "Other"),
    unknown: "var(--theme-foreground-muted)"
  }
});
```

```js

const data = [
  {
    x: 1,
    y: 1,
    state: "SE"
  },
  {
    x: 3,
    y: 3,
    state: "DK"
  }
]

const countries = Mutable(['SE']);
const addOrRemoveCountry = (country) => {
  if (countries.value.includes(country)) {
    countries.value = countries.value.filter((c) => c !== country);
  } else {
    countries.value = [...countries.value, country];
  }
}
```

```js
const addClick = (index, scales, values, dimensions, context, next) => {
  const el = next(index, scales, values, dimensions, context);
  const circles = el.querySelectorAll("circle");
  for (let i = 0; i < circles.length; i++) {
    const d = {index: index[i], x: values.channels.x.value[i], y: values.channels.y.value[i]};
    circles[i].addEventListener("click", () => {
      const code = data[d.index].state
      addOrRemoveCountry(code);
      // alert(`Added ${JSON.stringify(d)} (${d.x}, ${d.y})`);
      el.classList.add("selected");
    });
  }
  return el;
}
```

```js
countries
```

```js
// 2D plot with SE at (1,1)
function plot2D(data, {width}) {
  return Plot.plot({
    width,
    height: 300,
    // start at 0,0 go to 3,3
    x: {label: "x"},
    y: {label: "y"},
    marks: [
      Plot.ruleY([0]),
      Plot.dot(data, {x: "x", y: "y", fill: "state", size: 200, title: "state", render: addClick,
       r: 10, 
      className: `countrydot`
      }),
      Plot.text(data, {x: "x", y: "y", text: "state", dy: "-0.5em", dx: "-0.5em", color: "white", font: "bold 10px sans-serif", pointerEvents: "none"}),
      Plot.tip(olympians, Plot.pointer({
        x: "x",
        y: "y",
        title: (d) => d.state
      }))
    ]
  });
}
```

```js
plot2D(data, {width: 600})

```

```js
const pca_data = {
  Q1 : { 
    question_id: "Q1",
    question_pca: pcaQ1
  },
  Q2: { 
    question_id: "Q2",
    question_pca: pcaQ2
  },
  Q3: { 
    question_id: "Q3",
    question_pca: pcaQ3
  },
}

const question = view(Inputs.checkbox(["Q1", "Q2", "Q3"], {label: "question"}));

```

<div class="grid grid-cols-2">   
  <div class="card">
  ${question}
  </div>
  <div class="card">    
  ${resize((width) => {      
      const selectedPcaData = Object.values(pca_data)
        .filter((d) => question.includes(d.question_id))
        .map((d) => d.question_pca);
      if (selectedPcaData.length == 0){
        return pcaChart(pcaQ1, { width });
      }
      else{
      return pcaChart(selectedPcaData[0], { width });
      }
    })}
  </div>
</div>


```js
  function pcaChart(data, {width}) {
    return Plot.plot({
      title: "Choose a question to show the data, Q1 is shown by  default.",
      width,
      grid: true,
      x: {label: "Body mass (g)"},
      y: {label: "Flipper length (mm)"},
      color: {legend: true},
      marks: [
        //Plot.linearRegressionY(penguins, {x: "body_mass_g", y: "flipper_length_mm", stroke: "species"}),
        Plot.dot(data, {x: "PC1", y: "PC2", stroke: "Countries", tip: true})
      ]
    });
  }
```
<!-- Cards with big numbers -->

<div class="grid grid-cols-4">
  <div class="card">
    <h2>United States 🇺🇸</h2>
    <span class="big">${launches.filter((d) => d.stateId === "US").length.toLocaleString("en-US")}</span>
  </div>
  <div class="card">
    <h2>Russia 🇷🇺 <span class="muted">/ Soviet Union</span></h2>
    <span class="big">${launches.filter((d) => d.stateId === "SU" || d.stateId === "RU").length.toLocaleString("en-US")}</span>
  </div>
  <div class="card">
    <h2>China 🇨🇳</h2>
    <span class="big">${launches.filter((d) => d.stateId === "CN").length.toLocaleString("en-US")}</span>
  </div>
  <div class="card">
    <h2>Other</h2>
    <span class="big">${launches.filter((d) => d.stateId !== "US" && d.stateId !== "SU" && d.stateId !== "RU" && d.stateId !== "CN").length.toLocaleString("en-US")}</span>
  </div>
</div>

<!-- Plot of launch history -->

```js
function launchTimeline(data, {width} = {}) {
  return Plot.plot({
    title: "Launches over the years",
    width,
    height: 300,
    y: {grid: true, label: "Launches"},
    color: {...color, legend: true},
    marks: [
      Plot.rectY(data, Plot.binX({y: "count"}, {x: "date", fill: "state", interval: "year", tip: true})),
      Plot.ruleY([0])
    ]
  });
}
```

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => launchTimeline(launches, {width}))}
  </div>
</div>

<!-- Plot of launch vehicles -->

```js
function vehicleChart(data, {width}) {
  return Plot.plot({
    title: "Popular launch vehicles",
    width,
    height: 300,
    marginTop: 0,
    marginLeft: 50,
    x: {grid: true, label: "Launches"},
    y: {label: null},
    color: {...color, legend: true},
    marks: [
      Plot.rectX(data, Plot.groupY({x: "count"}, {y: "family", fill: "state", tip: true, sort: {y: "-x"}})),
      Plot.ruleX([0])
    ]
  });
}
```

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => vehicleChart(launches, {width}))}
  </div>
</div>

Data: Jonathan C. McDowell, [General Catalog of Artificial Space Objects](https://planet4589.org/space/gcat)
