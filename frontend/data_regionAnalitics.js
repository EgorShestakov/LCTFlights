export const regionAnalytics = {
    region_id: 23,
    region_name: "Алтайская область",
    period: {
        start_date: "2024-01-01",
        end_date: "2024-01-31"
    },
    summary: {
        total_flights: 150,
        successful_flights: 148,
        failed_flights: 2,
        total_duration_seconds: 405000,
        total_distance_meters: 2250000,
        avg_flight_duration: 2700,
        violations_count: 5,
        success_rate: 98.7
    },
    trends: {
        flights_by_day: {
            "2024-01-01": 15,
            "2024-01-02": 22,
            "2024-01-03": 18
        },
        flights_by_hour: {
            "8": 45,
            "9": 67,
            "10": 52
        }
    },
    by_operator: [
        {
            operator_id: "operator_7",
            operator_name: "Аэротехнологии",
            flights_count: 45,
            success_rate: 97.8,
            avg_duration: 2800
        }
    ],
    by_drone_model: [
        {
            model: "DJI Matrice 300",
            flights_count: 120,
            usage_percentage: 80.5
        }
    ],
    violations_analysis: {
        by_type: {
            max_altitude: 15,
            restricted_zone: 8,
            no_permission: 3
        },
        by_severity: {
            low: 5,
            medium: 15,
            high: 6
        },
        trend: {
            "2024-01-01": 2,
            "2024-01-02": 1,
            "2024-01-03": 3
        }
    }
};