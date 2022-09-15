// create nutrition pie charts using built-in canvas function
var xValues = ["fat (g)", "sat (g)", "Carbs (g)", "sugars (g)", "fibre (g)", 
"Protein (g)", "Salt (g)"];
var yValues = [fat, sat, carb, sugar, fibre, pro, salt];
var barColors = [
  "#fc0362",
  "#a649bf",
  "#4ca183",
  "#ad9951",
  "#518ead",
  "#f0edda",
  "#d9db5c"
];

new Chart("myChart", {
  type: "doughnut",
  data: {
    labels: xValues,
    datasets: [{
      backgroundColor: barColors,
      data: yValues
    }]
  },
  options: {
    title: {
      display: true,
      text: "Nutrition Overview: " + kcal +"kcal."
    }
  }
});
