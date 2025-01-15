---
theme: dashboard
title: European Attitudes 
toc: false
sidebar: false
---

<div class="hero">
  <h1>European Attitudes toward EU Energy Policies</h1>
  <h2>Each year, the EU gather each country's opinions in energy matters and the EU strategies. Use these graphs to explore where each country stands today, and compare the attitudes to other EU data, such as GDP, energy consumption, and more.</h2>
</div>

<style type="text/css">

.chip {
  display: inline-block;
  padding: 0.5rem 1rem;
  margin: 0.1rem;
  border-radius: 9999px;
  border: 1px solid #007BFF;
  background-color: #f8f9fa;
  color: #007BFF;
  cursor: pointer;
}

.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: var(--sans-serif);
  margin: 4rem 0 8rem;
  text-wrap: balance;
  text-align: center;
}

.hero h1 {
  margin: 1rem 0;
  padding: 1rem 0;
  max-width: none;
  font-size: 30px;
  font-weight: 500;
  line-height: 1;
  background: linear-gradient(30deg, var(--theme-foreground-focus), currentColor);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero h2 {
  margin: 0;
  max-width: 34em;
  font-size: 20px;
  font-style: initial;
  font-weight: 500;
  line-height: 1.5;
  color: var(--theme-foreground-muted);
}

.bottom-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: var(--sans-serif);
  margin: 4rem 0 8rem;
  text-wrap: balance;
  text-align: center;
}

.bottom-text h4 {
  min-width: 100%;
  padding-top: 4rem;
}



.countrydot {
  cursor: pointer;
}

.floating-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background-color: white;
  border-top: 1px solid #ccc;
  padding: 1rem;
  display: flex;
  justify-content: center;
  z-index: 1000;
}

.floating-bar-content {
  width: 80%;
}



</style>

<!-- Load and transform the data -->


```js

const EU27CodesToCountry = new Map(Object.entries({
  "AT": "Austria",
  "BE": "Belgium",
  "BG": "Bulgaria",
  "CY": "Cyprus",
  "CZ": "Czechia",
  "DE": "Germany",
  "DK": "Denmark",
  "EE": "Estonia",
  "EL": "Greece",
  "ES": "Spain",
  "FI": "Finland",
  "FR": "France",
  "HR": "Croatia",
  "HU": "Hungary",
  "IE": "Ireland",
  "IT": "Italy",
  "LT": "Lithuania",
  "LU": "Luxembourg",
  "LV": "Latvia",
  "MT": "Malta",
  "NL": "Netherlands",
  "PL": "Poland",
  "PT": "Portugal",
  "RO": "Romania",
  "SE": "Sweden",
  "SI": "Slovenia",
  "SK": "Slovakia",
  "UK": "United Kingdom",
  "EU27": "EU27"
}));

const countryNamesToEU27Codes = new Map(Array.from(EU27CodesToCountry.entries()).map(([k, v]) => [v, k]));



```

```js
const data = await FileAttachment("data/data_VOL_A.json").json()
const pca_data = await FileAttachment("data/pca_data.json").json()
const GDPWithMoreCountries = await FileAttachment("data/GDPs.csv").csv({typed: true});
const pricesWithMoreCountries = await FileAttachment("data/EnergyPrices.csv").csv({typed: true});
const prices = pricesWithMoreCountries.filter((d) => countryNamesToEU27Codes.has(d.geo));
const GDP = GDPWithMoreCountries.filter((d) => countryNamesToEU27Codes.has(d.geo));

let summarizedPrices = []

// Summarize prices data by year
const yearlyPrices = d3.group(prices, (d) => d.TIME_PERIOD.split('-')[0]); // Group by year
summarizedPrices = Array.from(yearlyPrices, ([year, values]) => ({
  time: +year,
  value: d3.mean(values, (d) => +d.OBS_VALUE) // Average of OBS_VALUE for S1 and S2
}));

// Get energy price per half-year for each country code
const energyPricesPerCountry = d3.group(prices, (d) => d.geo);
// Convert "TIME_PERIOD" that is "YEAR-S1" or "YEAR-S2" to "YEAR-01" or "YEAR-07"
const energyPricesPerCountryPerYear = Array.from(energyPricesPerCountry, ([country, values]) => {
  const prices = values.map((d) => {
    const year = d.TIME_PERIOD.split('-')[0];
    const month = d.TIME_PERIOD.split('-')[1] === "S1" ? "01" : "07";
    return {
      time: new Date(`${year}-${month}`),
      value: +d.OBS_VALUE
    }
  });
  const code = countryNamesToEU27Codes.get(country);
  return [code, prices.map((d) => ({...d, code}))];
});

const energyPricesPerCountryCode = new Map(energyPricesPerCountryPerYear);

const GDPPerCountry = d3.group(GDP, (d) => d.geo);
const GDPPerCountryPerYear = Array.from(GDPPerCountry, ([country, values]) => {
  const GDPs = values.map((d) => {
    return {
      // TIME_PERIOD is in the format "YEAR"
      time: new Date(`${d.TIME_PERIOD}-01-01`),
      value: +d.OBS_VALUE
    }
  });
  const code = countryNamesToEU27Codes.get(country);
  return [code, GDPs.map((d) => ({...d, code}))];
});

const GDPPerCountryCode = new Map(GDPPerCountryPerYear);

```

```js
const countries = Mutable(['EU27']);
const addOrRemoveCountry = (country) => {
  if (countries.value.includes(country)) {
    countries.value = countries.value.filter((c) => c !== country);
  } else {
    countries.value = [...countries.value, country];
  }
}

const addClick = (index, scales, values, dimensions, context, next) => {
  const el = next(index, scales, values, dimensions, context);
  const circles = el.querySelectorAll("circle");
  for (let i = 0; i < circles.length; i++) {
    const d = {index: index[i], x: values.channels.x.value[i], y: values.channels.y.value[i]};
    circles[i].addEventListener("click", (e) => {
      // This is a rather hacky way to get the country code
      const countryCode = values.channels.fill.value[i];
      addOrRemoveCountry(countryCode);
      // alert(`Added ${JSON.stringify(d)} (${d.x}, ${d.y})`);
      // el.classList.add("selected");
    });
  }
  return el;
}
```

```js

function plot2D(data, {width}) {
  return Plot.plot({
    width,
    // start at 0,0 go to 3,3
    x: {label: "PCA 1"},
    y: {label: "PCA 2"},
    grid: true,
    // color: {legend: false},
    marks: [
      Plot.ruleY([0]),
      Plot.dot(data, {
        x: "PC1", y: "PC2", r: 10, className: `countrydot`, render: addClick,
        fill: "Countries",
        fillOpacity: (d) => {
          return countries.includes(d.Countries) ? 1 : 0.5;
        } 
      }),
      // Add text labels for country names
      Plot.text(data, {x: "PC1", y: "PC2", text: "Countries", dx: 0, dy: 0, pointerEvents: "none"}),
        // Add horizontal and vertical lines through the origin
      Plot.ruleX([0], {stroke: "grey", strokeWidth: 2}),
      Plot.ruleY([0], {stroke: "grey", strokeWidth: 2}),
    ]
  });
}
```

```js
const questionTitlesMap = new Map(Object.entries(data)
  // Filter out questions that end with T
  .filter(([k, v]) => !k.endsWith("T"))
  .map(([k, v]) => [k, {...v, id: k}])
);


```

```js

// const questionTitlesListWithCategoryLabels = 
//   Object.entries(data)
//     .filter(([k, v]) => !k.endsWith("T"))
//     .map(([k, v]) => [k, {...v, id: k}])
//     .map(([k, v]) => {
//       const category = k.split("_")[0];
//       return [k, {...v, category, id: k}];
//     });


const selectedQuestion = view(
  Inputs.select(
    questionTitlesMap,
    {
      format: ([k, v]) => v.title,
      value: questionTitlesMap.get("QC1"),
      width: "100%"
    }
  )
);
```

```html
<h1 style="width: 100%; font-size: 1.5rem;  max-width: none;">
  ${selectedQuestion.title}
</h1>
<h2>
  ${selectedQuestion.subtitle}
</h2>

<!-- floating bar on bottom of the screen -->
<div class="floating-bar">
  <div class="floating-bar-content">
    <h3>Investigated question</h3>
    <div style="width: 80%">
      <b>
        ${selectedQuestion.title}
      </b>
      <div>
        ${selectedQuestion.subtitle}
      </div>
    </div>
  </div>
</div>
```

```html
<div class="chip-container">
  <!-- countries that can be selected / deselected -->
  ${EU27CodesToCountry.entries().map(([code, country]) => {
    return html`
      <button class="chip" style="background-color: ${countries.includes(code) ? "#007BFF" : "#f8f9fa"}; color: ${countries.includes(code) ? "#fff" : "#000"}" onclick=${() => addOrRemoveCountry(code)}>
        ${country}
      </button>
    `;
  })}
</div>

```


```html
<div class="grid grid-cols-2">
  <div class="card" id="histogram">
    ${resize((width) => plot2D(pca_data[selectedQuestion.id], {width}))}
  </div>
  <div class="card" id="histogram">
    ${resize((width) => plotHistogram(histogramData, {width}))}
  </div>
</div>
```

```js
// Load data_VOL_A.json

// Go through each question and for every table make sure that there are no "-" in the data, if there are, replace it with 0
Object.keys(data).forEach((question) => {
  const table = data[question].table;
  // Filter out the "Statement" key
  Object.keys(table).filter((d) => d !== "Statement").forEach((country) => {
    const values = table[country];
    table[country] = Object.entries(values).reduce((acc, [key, value]) => {
      acc[key] = value === "-" ? 0 : value;
      return acc;
    }, {});
  });
});


const selectedQuestionID = selectedQuestion.id;

const selectedData = data[selectedQuestionID];



// The data is found in the "table" key.
// The table exists of all countries (for example with a key "SE"), and then "Statement" which corresponds to the values inside each country. "Statement"[0] corresponds to country[0].

// Get countries and filter out the "Statement" key
const allCountries = Object.keys(selectedData.table).filter((d) => d !== "Statement");

// Get the statements
const statements = Object.values(selectedData.table["Statement"])



// Create a stacked histogram with each country as a bar (a row) and each statement as a segment (a stack)

const histogramData = pca_data[selectedQuestionID].sort((a, b) => b.PC1 - a.PC1).filter(d => d.Countries !== "UE27\nEU27").map((d, i) => {
  const country = d.Countries;
  return Object.entries(selectedData.table[country]).map(([statement, value]) => {
    return {country, statement: statements[parseInt(statement)], value, PC1: d.PC1, PC2: d.PC2};
  });
}).flat();

// Some questions have statements that can be used with a blue / orange color scheme
// For QC2, QC10, and QC11, they start with "Yes, " or "No, " and can be used with a blue / orange color scheme. "Yes, " is blue, "No, " is orange.
// The mapping of which shade of blue and orange can be devised by the order of the statements in the data.


const yesNoBlueOrangeColorScaleByQuestion = (questionID) => {
  const statements = Object.values(data[questionID].table["Statement"]);
  const yesStatements = statements.filter((statement) => statement.startsWith("Yes, ")).reverse();
  const noStatements = statements.filter((statement) => statement.startsWith("No, ")).reverse();

  // Adjust scales
  const blueRange = (t) => d3.interpolateBlues(0.3 + t * 0.7);
  const orangeRange = (t) => d3.interpolateOranges(0.3 + t * 0.7);

  const blueScale = d3.scaleSequential(blueRange).domain([0, yesStatements.length]);
  const orangeScale = d3.scaleSequential(orangeRange).domain([0, noStatements.length]);

  const result = statements.map((statement) => {
    if (statement.startsWith("Yes, ")) {
      return blueScale(yesStatements.indexOf(statement));
    } else if (statement.startsWith("No, ")) {
      return orangeScale(noStatements.indexOf(statement));
    } else if (statement === "Don't know") {
      return "lightgrey";
    } else {
      return "grey";
    }
  });

  return result;
};

const agreenessBlueOrangeColorScale = [
  d3.interpolateBlues(0.6),
  d3.interpolateBlues(0.3),
  d3.interpolateOranges(0.3),
  d3.interpolateOranges(0.6),
  "lightgrey",
  "grey"
];

const aLotALittleColorScale = [
  d3.interpolateBlues(0.8),
  d3.interpolateBlues(0.6),
  d3.interpolateBlues(0.4),
  d3.interpolateBlues(0.2),
  "lightgrey",
  "grey"
];


const rangeBySpecialQuestions = {
  QC2: yesNoBlueOrangeColorScaleByQuestion("QC2"),
  QC10: yesNoBlueOrangeColorScaleByQuestion("QC10"),
  QC11: yesNoBlueOrangeColorScaleByQuestion("QC11"),
  'QC3_1': agreenessBlueOrangeColorScale,
  'QC3_2': agreenessBlueOrangeColorScale,
  'QC3_3': agreenessBlueOrangeColorScale,
  'QC3_4': agreenessBlueOrangeColorScale,
  'QC3_5': agreenessBlueOrangeColorScale,
  'QC8_1': aLotALittleColorScale,
  'QC8_2': aLotALittleColorScale,
  'QC8_3': aLotALittleColorScale,
}

const plotHistogram = (
  data, {width}
) => {
  return Plot.plot({
    width,
    x: {label: "Country"},
    y: {tickFormat: "s", tickSpacing: 50, label: "Fraction of respondents"},
    color: {
      type: rangeBySpecialQuestions[selectedQuestionID] ? "ordinal" : "categorical",
      domain: statements,
      range: rangeBySpecialQuestions[selectedQuestionID],
      legend: true
    },
    marks: [
      Plot.barY(
        histogramData.filter(
          // Check if begins with "Total '"
          (d) => d.statement.startsWith("Total '") === false
        ),
        {
        x: "country",
        y: "value",
        fill: "statement",
        fillOpacity: (d) => {
          return countries.includes(d.country) ? 1 : 0.5;
        },
        channels: {PC1: {value: 'PC1'}},
        sort: {x: "PC1"}
        // sort: {color: null, x: "-y"}
      })
    ]
  })
}
```

```js

const selectedCountriesPriceData = countries.map((code => energyPricesPerCountryCode.get(code) ?? [])).flat();

function plotPrices(data, {width}) {
  return Plot.plot({
    title: "EU Energy Prices Over Time",
    width,
    height: 300,
    color: {
      legend: true,
      domain: countries,
    },
    y: {label: "Price (unit)", grid: true},
    marks: [
      Plot.line(data, {x: "time", y: "value", strokeWidth: 2, stroke: "code"}),
      Plot.dot(data, {x: "time", y: "value", fill: "code", r: 4})
    ]
  });
}
```

```html
<div class="grid grid-cols-2">
  <div class="card" id="prices">
    ${resize((width) => plotPrices(selectedCountriesPriceData, {width}))}
  </div>
  <div class="card" id="gdp">
    ${resize((width) => plotGDP(selectedCountriesGDPData, {width}))}
  </div>
</div>
```


```js

const selectedCountriesGDPData = countries.map((code => GDPPerCountryCode.get(code) ?? [])).flat();


function plotGDP(data, {width}) {
  return Plot.plot({
    title: "GDP Over Time",
    width,
    height: 300,
    color: {
      legend: true,
      domain: countries,
    },
    y: {label: "GDP (unit)", grid: true},
    marks: [
      Plot.line(data, {x: "time", y: "value", strokeWidth: 2, stroke: "code"}),
      Plot.dot(data, {x: "time", y: "value", fill: "code", r: 4})
    ]
  });
}

```


```js

// Load the energy data from both files
const energyConsumptionDataAllCountries = await FileAttachment("data/2020-2023_EU_energy_consumption.csv").csv({typed: true});
const energyProductionDataAllCountries = await FileAttachment("data/2020-2023_EU_energy_production.csv").csv({typed: true});

const energyConsumptionData = energyConsumptionDataAllCountries.filter((d) => countryNamesToEU27Codes.has(d.geo));

const energyProductionData = energyProductionDataAllCountries.filter((d) => countryNamesToEU27Codes.has(d.geo));

// Default year for both graphs
let selectedYear = 2022; 

// Color scale for energy sources (makes comparison easier)
const energySources = [...new Set([...energyConsumptionData, ...energyProductionData].map(d => d.siec))];
const sharedColorScale = Plot.scale({
  color: {
    type: "categorical",
    domain: energySources, 
    range: d3.schemeTableau10 
  }
});

// Year buttons
function yearButtons() {
  const uniqueYears = [...new Set(energyConsumptionData.map(d => d.TIME_PERIOD))].sort();
  const container = document.createElement("div");
  container.style.marginBottom = "20px";
  container.style.display = "flex";
  container.style.gap = "10px";

  uniqueYears.forEach(year => {
    const button = document.createElement("button");
    button.textContent = year;
    button.style.padding = "10px 15px";
    button.style.cursor = "pointer";
    button.style.border = "1px solid #007BFF";
    button.style.backgroundColor = year === selectedYear ? "#007BFF" : "#fff";
    button.style.color = year === selectedYear ? "#fff" : "#007BFF";
    button.style.borderRadius = "5px";
    button.onclick = () => {
      selectedYear = year;
      renderCharts(); // Re-render both charts when a year is selected
      updateButtonStyles(container); // Update button styles
    };
    container.appendChild(button);
  });

  return container;
}

// Button styles
function updateButtonStyles(container) {
  container.childNodes.forEach(button => {
    button.style.backgroundColor = button.textContent == selectedYear ? "#007BFF" : "#fff";
    button.style.color = button.textContent == selectedYear ? "#fff" : "#007BFF";
  });
}

// Filter, normalize, and render a chart
function renderChart(data, title) {
  // Filter data for the selected year
  const dataForYear = data.filter(
    d => d.TIME_PERIOD === selectedYear && d.geo !== "European Union - 27 countries (from 2020)" && d.siec !== "Total"
  );

  // Aggregate data by country and energy source
  const aggregatedData = d3.rollups(
    dataForYear,
    v => d3.sum(v, d => d.OBS_VALUE),
    d => d.geo,
    d => d.siec
  ).flatMap(([geo, siecData]) => 
    siecData.map(([siec, value]) => ({
      geo,
      siec,
      OBS_VALUE: value
    }))
  );

  // Normalize the data by total energy for each country
  const normalizedData = d3.group(aggregatedData, d => d.geo);
  const flattenedNormalizedData = Array.from(normalizedData, ([geo, records]) => {
    const total = d3.sum(records, d => d.OBS_VALUE); 
    return records.map(d => ({
      ...d,
      normalizedValue: d.OBS_VALUE / total 
    }));
  }).flat();

  // Normalized stacked bar chart function
  return Plot.plot({
    title: `${title} (Normalized, ${selectedYear})`,
    width: 1000, 
    height: 700,
    marginLeft: 100,
    marginBottom: 80,
    x: {
      label: "Country",
      axis: "bottom",
      domain: [...new Set(flattenedNormalizedData.map(d => d.geo))],
      tickRotate: -45 
    },
    y: {label: "Proportion of Total Energy", grid: true, domain: [0, 1]},
    color: {legend: true, ...sharedColorScale},
    marks: [
      Plot.barY(
        flattenedNormalizedData,
        Plot.groupX({y: "sum"}, {
          x: "geo", y: "normalizedValue", fill: "siec", title: d => `${d.siec}: ${(d.normalizedValue * 100).toFixed(1)}%`,
          fillOpacity: (d) => {
            const code = countryNamesToEU27Codes.get(d[0].geo)
            return countries.includes(code) ? 1 : 0.5;
          }
        })
      )
    ]
  });
}

// Render both charts
function renderCharts() {
  // Render production chart
  document.getElementById("productionChartContainer").innerHTML = ""; 
  document.getElementById("productionChartContainer").appendChild(
    resize((width) => renderChart(energyProductionData, "Energy Production"))
  );

  // Render consumption chart
  document.getElementById("consumptionChartContainer").innerHTML = ""; 
  document.getElementById("consumptionChartContainer").appendChild(
    resize((width) => renderChart(energyConsumptionData, "Energy Consumption"))
  );
}

// Add year buttons and render the initial charts
document.getElementById("yearButtonContainer").appendChild(yearButtons());
// renderCharts();

```

<div id="yearButtonContainer"></div>

```html
<h2>Energy Production</h2>
<div id="productionChartContainer">
  ${resize((width) => renderChart(energyProductionData, "Energy Production"))}
</div>
<h2>Energy Consumption</h2>
<div id="consumptionChartContainer">
  ${resize((width) => renderChart(energyConsumptionData, "Energy Consumption"))}
</div>

<div class="bottom-text">
<h4> This website was created by Douglas Bengtsson, Elena Bank, Julia Böckert & Pravesha Ramsundersingh.</h4>
</div>

```