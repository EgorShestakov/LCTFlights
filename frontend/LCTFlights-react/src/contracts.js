export const rootAPI = "http://localhost:3000";

export const contracts = {
    generateReport: rootAPI + "/reports/generate",
    // mapStats: rootApiUrl + "/map/stats",
    mapStats: rootAPI + "/flights_percent",
    flights: rootAPI + "/flights",
    postFile: rootAPI + "/post",
};