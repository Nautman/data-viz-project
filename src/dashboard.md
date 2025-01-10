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
const launches = FileAttachment("data/launches.csv").csv({typed: true});
const pcaQ1 = FileAttachment("data/PCAVOL_A_QC1.csv").csv({typed: true});
const pcaQ2 = FileAttachment("data/PCAVOL_A_QC2.csv").csv({typed: true});
const pcaQ3 = FileAttachment("data/PCAVOL_A_QC3_1.csv").csv({typed: true});
const data = await FileAttachment("data/data_VOL_A.json").json()

const all_questions = FileAttachment("data/questions.csv").csv({typed: true});
```
```js
const pca_data = {
  QC1: pcaQ1,
  QC2: pcaQ2,
  QC3: pcaQ3
};

const questions_to_display = ["QC1", "QC2", "QC3"];

const questions_to_display_dict = all_questions
  .filter((q) => questions_to_display.includes(q.ID))
  .map((q) => {
    return {
      question_id: q.ID || "Unknown ID",
      sub_id: q.SubID || "",
      text: q.Question_Text || "Unknown Text"
    };
  });

// console.log(all_questions);
// console.log(questions_to_display_dict);
// console.log(pca_data)

let user_selected_questions = [];

const handleCheckboxChange = (event) => {
  const questionId = event.target.value;
  if (event.target.checked) {
    user_selected_questions.push(questionId);
  } else {
    user_selected_questions = user_selected_questions.filter((id) => id !== questionId);
  }
  updatePcaChart();
};

const updatePcaChart = () => {
  const selectedPcaData = user_selected_questions.map((id) => pca_data[id]);
  const chartData = selectedPcaData.length > 0 ? selectedPcaData[0] : pcaQ1;
  // console.log(chartData[0]["Countries"])
  document.getElementById("pca-chart").innerHTML = "";
  document.getElementById("pca-chart").appendChild(pcaChart(chartData, { width: 600 }));
  
};
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
      Plot.text(data, {x: "PC1", y: "PC2", text: "Countries", dx: 5, dy: -5, pointerEvents: "none"}),
        // Add horizontal and vertical lines through the origin
      Plot.ruleX([0], {stroke: "grey", strokeWidth: 2}),
      Plot.ruleY([0], {stroke: "grey", strokeWidth: 2}),
      // Plot.dot(data, {x: "x", y: "y", fill: "state", size: 200, title: "state", render: addClick,
      //  r: 10, 
      // className: `countrydot`
      // }),
      // Plot.text(data, {x: "x", y: "y", text: "state", dy: "-0.5em", dx: "-0.5em", color: "white", font: "bold 10px sans-serif", pointerEvents: "none"}),
    ]
  });
}
```

```js
countries
```

```js
const questionTitlesMap = new Map(Object.entries(data).map(([k, v]) => [k, {...v, id: k}]).slice(0,8));
```

```js

const selectedQuestion = view(
  Inputs.radio(
    questionTitlesMap,
    {
      format: ([k, v]) => v.title,
      value: questionTitlesMap.get("QC1"),
    }
  )
);
```

```js
plot2D(
  pca_data[selectedQuestion.id]
  , {width: 600})
```

```html
<div class="grid grid-cols-2">
  <div class="card">
    ${questions_to_display_dict.map(
      (d) => html`<div style="display: flex; align-items: center;">
  <input
    type="checkbox"
    id="${d.question_id}"
    name="question"
    value="${d.question_id}"
    onchange=${(event) => handleCheckboxChange(event)}
  />
  <label for="${d.question_id}" style="margin-right: 10px;">${d.question_id}.${d.sub_id}</label>
  <p>${d.text}</p>
</div>`
    )}
  </div>
  <div class="card" id="pca-chart">
    ${pcaChart(pcaQ1, { width: 600 })}
  </div>
</div>
```

```js
  const user_selected_countries = []; // Store clicked dots here
  const selectedCountriesContainer = document.getElementById("countries");
    if (selectedCountriesContainer) {
      selectedCountriesContainer.innerHTML = "<p>Selected Countries will show up here</p>";
    } else {
      console.error("Container with ID 'countries' not found");
    }

  function pcaChart(data, {width}) {
    // Create the chart
    const chart = Plot.plot({
      title: "Choose a question to show the data, Q1 is shown by default.",
      width,
      grid: true,
      x: {label: "PCA 1"},
      y: {label: "PCA 2"},
      color: {legend: false},
      marks: [
        // Add dots with a fixed color
        Plot.dot(data, {x: "PC1", y: "PC2", fill: (d) => {
          // console.log("d", d.Countries, user_selected_countries)
            return user_selected_countries.includes(d.Countries) ? "lightblue" : "red";
          }, r: 10, className: `countrydot`
        }),
        // Add text labels for country names
        Plot.text(data, {x: "PC1", y: "PC2", text: "Countries", dx: 5, dy: -5, pointerEvents: "none"}),
        // Add horizontal and vertical lines through the origin
        Plot.ruleX([0], {stroke: "grey", strokeWidth: 2}),
        Plot.ruleY([0], {stroke: "grey", strokeWidth: 2}),
      ]
    });

    // Add interactivity
    const svg = chart.querySelector("svg");
    const dots = svg.querySelectorAll("circle"); // Select dots
    
    
    dots.forEach((dot, index) => {
      // Bind data to each dot
      dot.dataset.index = index;
      dot.dataset.pc1 = data[index].PC1;
      dot.dataset.pc2 = data[index].PC2;
      dot.dataset.country = data[index].Countries;

      // Add click event listener
      dot.addEventListener("click", (event) => {
        const target = event.target;
        const clickedData = {
          index: target.dataset.index,
          PC1: target.dataset.pc1,
          PC2: target.dataset.pc2,
          country: target.dataset.country,
        };
      // Check if the country is already selected
      const existingIndex = user_selected_countries.findIndex(
        (d) => d.country === clickedData.country
      );

      if (existingIndex === -1) {
        // If not, add it to the array
        user_selected_countries.push(clickedData);
      } else {
        // If yes, remove it from the array
        user_selected_countries.splice(existingIndex, 1);
      }

            // Update the UI dynamically
        selectedCountriesContainer.innerHTML = user_selected_countries
        .map((d) => `<div><p>${d.country}</p></div>`)
        .join("");
        // Perform an action (e.g., console log or update UI)
        console.log("Dot clicked:", clickedData);
        console.log("Selected Dots:", user_selected_countries)
      });
    });

    return chart;
  }
```

```html
<div class="grid grid-cols-1">
  <div class="card" id="countries">    
    <!-- This content is be replaced dynamically -->    
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

// console.log(pca_data[selectedQuestionID].sort((a, b) => b.PC1 - a.PC1))

const histogramData = pca_data[selectedQuestionID].sort((a, b) => b.PC1 - a.PC1).filter(d => d.Countries !== "UE27\nEU27").map((d, i) => {
  const country = d.Countries;
  return Object.entries(selectedData.table[country]).map(([statement, value]) => {
    return {country, statement: statements[parseInt(statement)], value, PC1: d.PC1, PC2: d.PC2};
  });
}).flat();

// console.log("histogramData", histogramData)
// console.log("statements", statements)


const chart = Plot.plot({
  width: 928,
  height: 500,
  x: {label: null},
  y: {tickFormat: "s", tickSpacing: 50},
  color: {
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
```

```js
chart
```

```html
<div class="grid grid-cols-1">
  <div class="card" id="histogram">    
    <!-- This content is be replaced dynamically -->    
  </div>
</div>
```

```js
// document.getElementById("histogram").appendChild(chart);
```





