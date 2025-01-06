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




<!-- Energy Consumption Graph -->

```js

// Load the energy data from the CSV file
const energy_data = await FileAttachment("data/2020-2023_EU_energy_consumption.csv").csv({typed: true});

// Get unique energy sources and years
const uniqueSources = [...new Set(energy_data.map(d => d.siec))];
const uniqueYears = [...new Set(energy_data.map(d => d.TIME_PERIOD))].sort(); // Sort years for proper order

// Initialize selected year and energy source
let selectedYear = 2022; // Default year
let selectedSource = "Solid fossil fuels"; // Default energy source

// Find the dashboard div
const dashboardDiv = document.getElementById("energy-dashboard");

// Create a container for the title, dropdowns, and graph
const container = document.createElement("div");

// Add a title above the dropdowns
const title = document.createElement("h2");
title.textContent = "Energy Consumption per EU Country";
title.style.marginBottom = "10px";
title.style.fontSize = "18px";
title.style.fontWeight = "bold";
container.appendChild(title);

// Create the year dropdown menu
const yearDropdown = document.createElement("select");
yearDropdown.style.marginBottom = "10px";
yearDropdown.style.marginRight = "20px";
yearDropdown.style.padding = "8px 12px";
yearDropdown.style.fontSize = "16px";
yearDropdown.style.border = "1px solid #007BFF";
yearDropdown.style.borderRadius = "5px";

// Populate the year dropdown
uniqueYears.forEach(year => {
  const option = document.createElement("option");
  option.value = year;
  option.textContent = year;
  if (year === selectedYear) option.selected = true;
  yearDropdown.appendChild(option);
});

// Year dropdown change event
yearDropdown.onchange = () => {
  selectedYear = +yearDropdown.value; // Update the selected year
  renderGraph(); // Re-render the graph when a new year is selected
};

// Create the energy source dropdown menu
const sourceDropdown = document.createElement("select");
sourceDropdown.style.marginBottom = "20px";
sourceDropdown.style.padding = "8px 12px";
sourceDropdown.style.fontSize = "16px";
sourceDropdown.style.border = "1px solid #007BFF";
sourceDropdown.style.borderRadius = "5px";

// Populate the energy source dropdown
uniqueSources.forEach(source => {
  const option = document.createElement("option");
  option.value = source;
  option.textContent = source;
  if (source === selectedSource) option.selected = true;
  sourceDropdown.appendChild(option);
});

// Energy source dropdown change event
sourceDropdown.onchange = () => {
  selectedSource = sourceDropdown.value; // Update the selected energy source
  renderGraph(); // Re-render the graph when a new source is selected
};

// Add the dropdowns to the container
container.appendChild(yearDropdown);
container.appendChild(sourceDropdown);

// Create a container for the graph
const graphContainer = document.createElement("div");
container.appendChild(graphContainer);

// Append the entire container to the dashboard div
dashboardDiv.appendChild(container);

// Define the graph rendering function
function renderGraph() {
  // Filter data for the selected energy source across all years
  const dataForSource = energy_data.filter(d => d.siec === selectedSource && d.geo !== "European Union - 27 countries (from 2020)");
  
  // Get the maximum OBS_VALUE for the selected energy source
  const maxConsumption = d3.max(dataForSource, d => d.OBS_VALUE);

  // Filter data for the selected year and energy source
  const filteredData = dataForSource.filter(d => d.TIME_PERIOD === selectedYear);

  // Calculate the average energy consumption for the selected year
  const averageConsumption = d3.mean(filteredData, d => d.OBS_VALUE);
  const extendedData = [...filteredData, {geo: "EU Average", OBS_VALUE: averageConsumption}];

  // Render the graph using Plot
  const plot = Plot.plot({
    title: `Energy Consumption by Country (${selectedSource}, ${selectedYear})`,
    width: 800,
    height: 600,
    marginLeft: 100,
    x: {
      label: "Energy Consumption (Thousand Tonnes of Oil Equivalent)",
      grid: true,
      domain: [0, maxConsumption] // Set consistent axis maximum for all years
    },
    y: {label: "Country", domain: extendedData.map(d => d.geo), axis: "left", tickSize: 5},
    marks: [
      Plot.barX(filteredData, {
        x: "OBS_VALUE",
        y: "geo",
        fill: "steelblue",
        title: d => `${d.geo}: ${d.OBS_VALUE.toFixed(1)}` // Tooltip for individual countries
      }),
      Plot.barX([{geo: "EU Average", OBS_VALUE: averageConsumption}], {
        x: "OBS_VALUE",
        y: "geo",
        fill: "orange",
        title: d => `EU Average: ${d.OBS_VALUE.toFixed(1)}` // Tooltip for EU Average
      })
    ]
  });

  // Clear previous graph and append the new one
  graphContainer.innerHTML = "";
  graphContainer.appendChild(plot);
}

// Initial render
renderGraph();

```
<div id="energy-dashboard"></div>