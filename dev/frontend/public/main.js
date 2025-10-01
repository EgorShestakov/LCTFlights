const regions = document.querySelectorAll("path.region");
var totalDroneCount = 0;
var regionsInfo = {};

const rootUrl = "http://127.0.0.1:3000";

const contracts = {
    update_url: rootUrl + "/flights_percent"
};

/* const accentColors = {
    70: "red",
    50: "orange",
    30: "yello",
    5: "green",
    0: "gray",
}; */

function getColor(percent) {
    if (percent >= 10) return "red";
    else if (percent >= 3) return "orange";
    else if (percent >= 1.5) return "yellow";
    else if (percent >= 1) return "green";
    else return "gray";
}

regions.forEach((element) => element.onmouseenter = e => { // onmouseenter
    document.querySelector('h1#cursor_reg').innerHTML = e.target.attributes["data-title"].nodeValue + `\t(${e.target.attributes["reg-num"]?.nodeValue})`;
});

regions.forEach((element) => element.onclick = e => { // onmouseenter
    // console.log(e);
    console.log(e.target.attributes["reg-num"]?.nodeValue);
    console.log(window.regionsInfo);
    document.querySelector('h1#region_name').innerHTML = e.target.attributes["data-title"]?.nodeValue || "��� ������";
    const regNum = Number(e.target.attributes["reg-num"]?.nodeValue) || -1;
    document.querySelector('div#drone_count').innerHTML = "����� ����:\t" + (regionsInfo[regNum]?.drone_count || "��� ����������");

    if (totalDroneCount != 0) {
        document.querySelector('div#attack_persent').innerHTML = "�� ������ ����� ����:\t" + (((regionsInfo[regNum]?.drone_count || 0) / totalDroneCount) * 100).toFixed(2) + "%";
    } else {
        document.querySelector('div#attack_persent').innerHTML = "��� ������ � % ����";
    }
});

function update() {
    fetch(contracts.update_url, {
        methods: "GET",

    })
        .then(r => r.json())
        .then(data => {
            // console.log(data);
            window.regionsInfo = data;
            // console.log("response:");
            // console.log(window.regionsInfo);
            window.totalDroneCount = 0;
            for (const key in window.regionsInfo) {
                window.totalDroneCount += window.regionsInfo[key]?.drone_count;
            }
            // ���������� �����;
            regions.forEach(i => {
                // ���� �� ������ ����������� �����������
                const regNum = i.attributes["reg-num"]?.nodeValue || -1; // ������
                const persent = window.regionsInfo[regNum]?.drone_count;
                console.log(persent);
                const color = getColor(persent);
                // console.log(color);
                i["style"].fill = color;
            });
        });
}

document.querySelector("button#test").addEventListener("click", update);

/* document.querySelector("button#test").addEventListener("click", () => regions.forEach(i => {
    /!*  if (i.attributes['data-title'].nodeValue.includes("������")){
         console.log("����� ������")
         i["style"].fill = "red";
     }    // ������������ *!/
    console.log(i.attributes["data-title"]);
})); */