# JIVAS Command Line Interface (JVCLI)

![GitHub release (latest by date)](https://img.shields.io/github/v/release/TrueSelph/jvcli)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/TrueSelph/jvcli/test-jvcli.yaml)
![GitHub issues](https://img.shields.io/github/issues/TrueSelph/jvcli)
![GitHub pull requests](https://img.shields.io/github/issues-pr/TrueSelph/jvcli)
![GitHub](https://img.shields.io/github/license/TrueSelph/jvcli)

`jvcli` is a powerful command-line interface tool designed to streamline interactions with the Jivas Package Repository ([https://jpr.trueselph.com/](https://jpr.trueselph.com/)). It simplifies package management, user authentication, and namespace operations, ensuring seamless software development and deployment. It allows you to create, publish, update, download, and get information about various resources such as actions and agents.

## Installation

To install `jvcli`, use `pip`:

```sh
pip install jvcli
```

## Usage

To use `jvcli`, you need to log in first:

```sh
jvcli login
```

After logging in, you can use any of the available commands. For example, to create a new action:

```sh
jvcli create action --name my_action --version 0.0.1 --description "My first action"
```

To publish an action:

```sh
jvcli publish action --path ./my_action --visibility public
```

To start a new project:

```sh
jvcli startproject my_project
```

For more detailed usage, refer to the help command:

```sh
jvcli --help
```

## 🔰 Contributing

- **🐛 [Report Issues](https://github.com/TrueSelph/jvcli/issues)**: Submit bugs found or log feature requests for the `jvcli` project.
- **💡 [Submit Pull Requests](https://github.com/TrueSelph/jvcli/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/TrueSelph/jvcli
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details open>
<summary>Contributor Graph</summary>
<br>
<p align="left">
    <a href="https://github.com/TrueSelph/jvcli/graphs/contributors">
        <img src="https://contrib.rocks/image?repo=TrueSelph/jvcli" />
   </a>
</p>
</details>

## 🎗 License

This project is protected under the Apache License 2.0. See [LICENSE](./LICENSE) for more information.
