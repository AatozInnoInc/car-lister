using car_lister.Models;

namespace car_lister.Services;

public class VehicleMetaMapper
{
    public static readonly List<string> FacebookColors = new List<string>
    {
        "Black", "Blue", "Brown", "Gold", "Green", "Gray", "Pink", "Purple",
        "Red", "Silver", "Orange", "White", "Yellow", "Charcoal", "Off white",
        "Tan", "Beige", "Burgundy", "Turquoise"
    };

    public static readonly List<string> BodyStyles = new List<string>
    {
        "Sedan", "SUV", "Truck", "Coupe", "Convertible", "Hatchback",
        "Wagon", "Minivan", "Small Car", "Other"
    };

    public VehicleMeta MapFromCar(ScrapedCar car)
    {
        return new VehicleMeta
        {
            ExteriorColor = MapColor(car.ExteriorColor),
            InteriorColor = MapColor(car.InteriorColor),
            BodyStyle = MapBodyStyle(car.BodyStyle)
        };
    }

    public ScrapedCar ApplyMetaToCar(ScrapedCar car, VehicleMeta meta)
    {
        if (meta == null) return car;
        if (!string.IsNullOrWhiteSpace(meta.ExteriorColor)) car.ExteriorColor = meta.ExteriorColor;
        if (!string.IsNullOrWhiteSpace(meta.InteriorColor)) car.InteriorColor = meta.InteriorColor;
        if (!string.IsNullOrWhiteSpace(meta.BodyStyle)) car.BodyStyle = meta.BodyStyle;
        return car;
    }

    public string MapColor(string? originalColor)
    {
        var c = (originalColor ?? string.Empty).Trim();
        if (string.IsNullOrEmpty(c)) return "";
        var s = c.ToLowerInvariant();
        if (s.Contains("black") || s.Contains("ebony")) return "Black";
        if (s.Contains("white")) return "White";
        if (s.Contains("gray") || s.Contains("grey") || s.Contains("charcoal")) return "Gray";
        if (s.Contains("red") || s.Contains("crimson") || s.Contains("burgundy")) return "Red";
        if (s.Contains("blue") || s.Contains("navy")) return "Blue";
        if (s.Contains("brown") || s.Contains("bronze")) return "Brown";
        if (s.Contains("green")) return "Green";
        if (s.Contains("orange")) return "Orange";
        if (s.Contains("yellow") || s.Contains("gold")) return "Yellow";
        if (s.Contains("silver")) return "Silver";
        if (s.Contains("beige") || s.Contains("tan")) return "Beige";
        if (s.Contains("purple")) return "Purple";
        if (s.Contains("pink")) return "Pink";
        if (s.Contains("turquoise") || s.Contains("teal")) return "Turquoise";
        return c;
    }

    public string MapBodyStyle(string? originalStyle)
    {
        var v = (originalStyle ?? string.Empty).Trim();
        if (string.IsNullOrEmpty(v)) return "";
        var s = v.ToLowerInvariant();
        if (s.Contains("pickup") || s.Contains("pick-up") || s.Contains("pick up") || s.Contains("truck") ||
            s.Contains("crew cab") || s.Contains("regular cab") || s.Contains("extended cab") || s.Contains("quad cab") ||
            s.Contains("supercrew") || s.Contains("super cab") || s.Contains("king cab") || s.Contains("double cab") ||
            s.Contains("mega cab") || s.Contains("crewmax") || s.Contains("cab & chassis") || s.Contains("cab and chassis") ||
            s.Contains("chassis cab") || s.Contains("stepside") || s.Contains("f-") || s.Contains("ram ") ||
            s.Contains("silverado") || s.Contains("sierra")) return "Truck";
        if (s.Contains("suv") || s.Contains("sport utility") || s.Contains("sport-utility") || s.Contains("crossover") ||
            s.Contains("cross-over") || s.Contains("cuv") || s.Contains("ute") || s.Contains("sport ute")) return "SUV";
        if (s.Contains("sedan") || s.Contains("4-door") || s.Contains("4 door") || s.Contains("saloon")) return "Sedan";
        if (s.Contains("coupe") || s.Contains("2-door") || s.Contains("2 door") || s.Contains("2dr") || s.Contains("2 d") ||
            s.Contains("two-door") || s.Contains("two door") || s.Contains("fastback") || s.Contains("hardtop") || s.Contains("notchback")) return "Coupe";
        if (s.Contains("convertible") || s.Contains("cabriolet") || s.Contains("roadster") || s.Contains("spyder")) return "Convertible";
        if (s.Contains("hatchback") || s.Contains("hatch") || s.Contains("liftback") || s.Contains("sportback")) return "Hatchback";
        if (s.Contains("wagon") || s.Contains("estate") || s.Contains("touring") || s.Contains("shooting brake")) return "Wagon";
        if (s.Contains("minivan") || s.Contains("mini-van") || s.Contains("passenger van") || s.Contains("mpv")) return "Minivan";
        if (s.Contains("cargo van")) return "Other";
        if (s.Contains("compact") || s.Contains("subcompact") || s.Contains("micro") || s.Contains("city car") || s.Contains("mini")) return "Small Car";
        return v;
    }
}