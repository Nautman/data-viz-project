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

console.log(all_questions);
console.log(questions_to_display_dict);
console.log(pca_data)

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
  console.log(chartData[0]["Countries"])
  document.getElementById("pca-chart").innerHTML = "";
  document.getElementById("pca-chart").appendChild(pcaChart(chartData, { width: 600 }));
  
};
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
        Plot.dot(data, {x: "PC1", y: "PC2", fill: "blue", r: 10}),
        // Add text labels for country names
        Plot.text(data, {x: "PC1", y: "PC2", text: "Countries", dx: 5, dy: -5}),
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


