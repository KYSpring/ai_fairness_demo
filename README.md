# LLM Fairness Analysis Tool

A Vue 3 and Vite-based tool for conducting fairness analysis on Large Language Models (LLMs). This tool allows users to upload experimental data, select different analysis dimensions, and initiate a fairness evaluation. Upon completion of the evaluation, users can view detailed analysis results.

## Features

- Data Upload: Supports both auto-generated data and local data upload modes.
- Analysis Dimensions: Provides a variety of analysis dimension tags for users to choose from.
- Fairness Evaluation: Displays evaluation progress and shows results upon completion.
- Result Presentation: Presents consistency analysis, bias analysis, and unfair inaccuracy analysis results in tabular form.
- Dynamic Tag Scrolling: Analysis dimension tags support seamless scrolling animations.

## Technology Stack

- Frontend Framework: Vue 3
- Build Tool: Vite
- Component Library: TDesign Vue Next
- Icon Library: TDesign Icons Vue Next
- State Management: Vue Composition API (Reactivity)

## Installation and Usage

1. Go to the Frontend repository:
   git clone https://github.com/your-username/llm-fairness-analysis.git
   cd ai_fairness_frontend

2. Install dependencies:
   npm install

3. Start the development server:
   npm run dev

4. Build for production:
   npm run build

5. Preview the build:
   npm run preview

## Directory Structure

llm-fairness-analysis/
├── public/               # Static assets directory
│   └── vite.svg
├── src/                  # Source code directory
│   ├── assets/            # Static resources
│   ├── components/        # Vue components
│   ├── App.vue            # Root component
│   ├── main.ts            # Entry file
│   └── vite-env.d.ts
├── .gitignore            # Git ignore file configuration
├── package.json           # Project configuration file
├── README.md              # Project description file
└── tsconfig.json          # TypeScript configuration file

## Contributing

Contributions are welcome! Please submit Pull Requests or report Issues.

## License

MIT License

---

Special thanks to Tsinghua University Institute for AI and Law (THUIAIL) for their support and guidance.
