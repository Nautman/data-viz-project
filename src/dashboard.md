---
theme: dashboard
title: European Attitudes 
toc: false
---


<style type="text/css">


.countrydot {
  cursor: pointer;
}

</style>

<!-- Load and transform the data -->


```js

const EU27CodesToCountry = new Map(Object.entries({
  "AT": "Austria",
  "BE": "Belgium",
  "BG": "Bulgaria",
  "CY": "Cyprus",
  "CZ": "Czech Republic",
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
const GDP = await FileAttachment("data/GDPs.csv").csv({typed: true});
const pricesWithMoreCountries = await FileAttachment("data/EnergyPrices.csv").csv({typed: true});
const prices = pricesWithMoreCountries.filter((d) => countryNamesToEU27Codes.has(d.geo));

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

```

```js
const countries = Mutable(['SE']);
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
    height: 300,
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

const selectedQuestion = view(
  Inputs.select(
    questionTitlesMap,
    {
      format: ([k, v]) => v.title,
      value: questionTitlesMap.get("QC1"),
    }
  )
);
```


```html
<div class="grid grid-cols-1">
  <div class="card" id="histogram">
    ${resize((width) => plot2D(pca_data[selectedQuestion.id], {width}))}
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

```html
<div class="grid grid-cols-1">
  <div class="card" id="histogram">
    ${resize((width) => plotHistogram(histogramData, {width}))}
  </div>
</div>
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
<div class="grid grid-cols-1">
  <div class="card" id="prices">
    ${resize((width) => plotPrices(selectedCountriesPriceData, {width}))}
  </div>
</div>
```
