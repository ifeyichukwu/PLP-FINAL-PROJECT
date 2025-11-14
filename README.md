# Global EcoFootprint Calculator - https://ecofootprint.streamlit.app/

A Streamlit-based web application that calculates and visualizes personal carbon footprints with region-specific calculations for Global and African contexts.

## Project Overview
The Global EcoFootprint Calculator helps users understand their environmental impact by calculating their annual carbon footprint based on lifestyle choices. It provides specialized calculations for both global users and African contexts, considering regional differences in energy sources and lifestyle patterns.

## Features
The project includes the following key functionalities:
- **Region-Specific Calculations**: Tailored carbon footprint calculations for Global and African contexts, including country-specific electricity grid emission factors
- **Comprehensive Impact Assessment**: Analyzes carbon emissions across three main categories:
  - Housing (electricity, cooking gas, heating)
  - Transport (car, motorcycle, public transport, flights)
  - Diet (various dietary patterns)
- **Interactive Visualization**: Dynamic charts showing breakdown of carbon footprint using Plotly
- **Personalized Recommendations**: Custom suggestions for reducing carbon footprint based on user's results

## How to Run
1. Clone the repository:
    ```bash
    git clone <repository-url>
    ```
2. Navigate to the project directory:
    ```bash
    cd PLP-FINAL-PROJECT
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Run the Streamlit app:
    ```bash
    streamlit run global.py
    ```

## Requirements
- Python 3.x
- Required packages:
  - streamlit
  - pandas
  - plotly.express

## Technical Details
- Uses regional emission factors for accurate calculations
- Implements dynamic user interface with Streamlit
- Provides real-time calculations and visualizations
- Includes data validation and user guidance

## About the Project
This project was developed as part of the PLP Academy - AI for Software Engineering module. It demonstrates the practical application of:
- Python programming
- Web application development with Streamlit
- Data visualization
- Environmental impact calculations
- Region-specific adaptations

## Contribution
Feel free to fork the repository and submit pull requests for improvements or bug fixes. Areas for potential enhancement include:
- Adding more country-specific data
- Expanding the recommendation system
- Implementing additional visualization options

## License
This project is licensed under the LICENSE.

## Acknowledgments
- PLP Academy instructors for guidance
- EPA and DEFRA for emission factors data
- African regional energy data sources

## Author
Gospel Arinze
PLP Academy - AI for Software Engineering Module



