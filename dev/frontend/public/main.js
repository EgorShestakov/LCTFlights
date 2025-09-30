const regions = document.querySelectorAll("path.region");
var regionsInfo = {};

function getColor(percent) {
    if (percent >= 60) return "red";
    else if (percent >= 40) return "orange";
    else if (percent >= 10) return "yellow";
    else if (percent >= 1) return "green";
    else return "gray";
}

regions.forEach((element) => element.onmouseenter = e => {
    document.querySelector('h1#cursor_reg').innerHTML = e.target.attributes["data-title"].nodeValue + `\t(${e.target.attributes["reg-num"]?.nodeValue})`;
});

regions.forEach((element) => element.onclick = e => {
    document.querySelector('h1#region_name').innerHTML = e.target.attributes["data-title"]?.nodeValue || "Нет данных";
    const regNum = Number(e.target.attributes["reg-num"]?.nodeValue) || -1;
    document.querySelector('div#drone_count').innerHTML = "Число атак:\t" + (regionsInfo.region_distribution?.[regNum] || "нет информации");
    // Assume region_distribution has region_name: percent
});

document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        regionsInfo = data;
        regions.forEach(i => {
            const regNum = i.attributes["reg-num"]?.nodeValue || -1;
            const percent = regionsInfo.region_distribution[regNum] || 0;  // Adjust if keys are names
            const color = getColor(percent);
            i.style.fill = color;
        });
    });
});
