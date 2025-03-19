# Courtroom-FND: A Multi-Role Fake News Detection Method Based on Argument Switching-based Courtroom Debate

## Overview

Courtroom-FND is a novel multi-role fake news detection framework inspired by courtroom debates. This framework leverages large language models (LLMs) to simulate a structured debate process, where different roles (Prosecution, Defense, and Judge) engage in iterative discussions to determine the authenticity of news content. By incorporating role switching and iterative evaluations, Courtroom-FND enhances the accuracy, reliability, and explainability of fake news detection.

## Key Features

- **Multi-Role Interaction**: Simulates a courtroom debate with roles for Prosecution, Defense, and Judge.
- **Argument Switching**: Forces roles to argue from opposing perspectives, reducing bias and uncovering hidden inconsistencies.
- **Iterative Evaluation**: Conducts multiple rounds of debate to ensure a comprehensive assessment of news authenticity.
- **Explainability**: Provides transparent reasoning processes by simulating human-like debate and decision-making.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Courtroom-FND.git
   cd Courtroom-FND
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   ```bash
   export OPENAI_API_KEY='your-openai-api-key'
   ```

## Usage

### Running the Debate

To run the debate on a sample input, use the following command:
   ```bash
python code/courtroomdebate4fnd.py -i data/FakeNewsDataset/input.example.txt -o data/FakeNewsDataset/output -k your-openai-api-key
   ```

### Interactive Mode
For an interactive session where you can input your own news articles for detection, run:
```bash
python code/interactive.py
```

## Project Structure

```
Courtroom-FND/
├── code/
│   ├── __init__.py
│   ├── agent.py
│   ├── config4fnd.json
│   ├── openai_utils.py
│   ├── courtroomdebate4fnd.py
│   └── interactive.py
├── data/
│   ├── FakeNewsDataset/
│   └── CIAR.json
├── imgs/
├── courtroomdebate4fnd.sh
├── LICENSE
├── README.md
└── requirements.txt
```

## Configuration

The `config4fnd.json` file contains the prompts and configurations for the debate process. You can modify this file to customize the behavior of the Prosecution, Defense, and Judge roles.

## Contributing

We welcome contributions to improve Courtroom-FND. Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push to your branch.
4. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the GNU General Public License v3.0 License. See the [LICENSE](LICENSE) file for more details.

## Kind Reminder
This project is built based on the [Multi-Agents-Debate](https://github.com/Skytliang/Multi-Agents-Debate) repository, which is licensed under the GNU General Public License v3.0. We have modified and extended the original work to create Courtroom-FND, and this project is also released under the same license. Please refer to the original repository for more details on the base implementation.

## Citation

If you use Courtroom-FND in your research, please cite our work:


```bibtex
@article{Anonymous2023courtroomfnd,
  title={Courtroom-FND: A Multi-Role Fake News Detection Method Based on Argument Switching-based Courtroom Debate},
  author={Anonymous},
  journal={Journal of King Saud University Computer and Information Sciences},
  year={TBD, To Be Determined},
  publisher={TBD, To Be Determined}
}
```
