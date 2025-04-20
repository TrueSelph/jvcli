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

## Command Reference

Here's a comprehensive guide to all available JVCLI commands:

### Authentication Commands

#### `jvcli login`
Login to the Jivas Package Repository.

```sh
jvcli login
```

#### `jvcli signup`
Create a new account on the Jivas Package Repository.

```sh
jvcli signup
```

#### `jvcli logout`
Log out from the Jivas Package Repository.

```sh
jvcli logout
```

### Project Management

#### `jvcli startproject`
Create a new Jivas project with scaffolding.

```sh
jvcli startproject my_project
# With specific version
jvcli startproject my_project --version 2.0.0
# Without .env file
jvcli startproject my_project --no-env
```

Options:
- `--version`: Jivas project version to use for scaffolding (default: latest)
- `--no-env`: Skip generating the .env file

#### `jvcli clean`
Clean the Jac files in the current directory and subdirectories.

```sh
jvcli clean
```

### Create Commands

#### `jvcli create action`
Create a new action with its folder structure and files.

```sh
jvcli create action --name custom_action
# With more options
jvcli create action --name custom_action --version 1.0.0 --description "A custom action" --type interact_action --path ./my_actions
```

Options:
- `--name`: Name of the action (must be snake_case)
- `--version`: Version of the action (default: 0.0.1)
- `--jivas_version`: Version of Jivas (default: latest supported)
- `--description`: Description of the action
- `--type`: Type of action (action, interact_action, vector_store_action)
- `--singleton`: Indicate if the action is singleton (default: true)
- `--path`: Directory to create the action folder in (default: ./actions)
- `--namespace`: Namespace for the action (default: from token)

#### `jvcli create agent`
Create a new agent with its folder and associated files.

```sh
jvcli create agent --name custom_agent
# With more options
jvcli create agent --name custom_agent --version 1.0.0 --description "A custom agent" --path ./my_agents
```

Options:
- `--name`: Name of the agent (must be snake_case)
- `--version`: Version of the agent (default: 0.0.1)
- `--jivas_version`: Version of Jivas (default: latest supported)
- `--description`: Description of the agent (default: "A jivas agent autocreated by the jvcli")
- `--path`: Directory to create the agent (default: ./daf)
- `--namespace`: Namespace for the agent (default: from token)

#### `jvcli create namespace`
Create a new namespace through the API.

```sh
jvcli create namespace --name my-namespace
```

Options:
- `--name`: Name of the namespace

### Publish Commands

#### `jvcli publish action`
Publish an action to the Jivas environment.

```sh
jvcli publish action --path ./actions/my_action
# With visibility option
jvcli publish action --path ./actions/my_action --visibility private
# Generate package only without publishing
jvcli publish action --path ./actions/my_action --package-only --output ./packages
```

Options:
- `--path`: Path to the directory containing the action to publish
- `--visibility`: Visibility of the published action (public/private, default: public)
- `--package-only`: Only generate the package without publishing
- `--output`, `-o`: Output path for generated package
- `--namespace`: Namespace of the package (required when --path is a tarball)

#### `jvcli publish agent`
Publish an agent to the Jivas environment.

```sh
jvcli publish agent --path ./daf/my_agent
# With visibility option
jvcli publish agent --path ./daf/my_agent --visibility private
# Generate package only without publishing
jvcli publish agent --path ./daf/my_agent --package-only --output ./packages
```

Options:
- `--path`: Path to the directory containing the agent to publish
- `--visibility`: Visibility of the published agent (public/private, default: public)
- `--package-only`: Only generate the package without publishing
- `--output`, `-o`: Output path for generated package
- `--namespace`: Namespace of the package (required when --path is a tarball)

### Download Commands

#### `jvcli download action`
Download a JIVAS action package.

```sh
jvcli download action my_namespace/custom_action
# With specific version
jvcli download action my_namespace/custom_action 1.0.0
# With custom path
jvcli download action my_namespace/custom_action --path ./my_custom_actions
```

Options:
- `name`: Name of the action to download
- `version`: Version of the action (optional, default: latest)
- `--path`: Directory to download the action (optional)

#### `jvcli download agent`
Download a JIVAS agent package.

```sh
jvcli download agent my_namespace/custom_agent
# With specific version
jvcli download agent my_namespace/custom_agent 1.0.0
# With custom path
jvcli download agent my_namespace/custom_agent --path ./my_custom_agents
```

Options:
- `name`: Name of the agent to download
- `version`: Version of the agent (optional, default: latest)
- `--path`: Directory to download the agent (optional)

### Info Commands

#### `jvcli info action`
Get information about an action package.

```sh
jvcli info action my_namespace/custom_action
# With specific version
jvcli info action my_namespace/custom_action 1.0.0
```

Options:
- `name`: Name of the action
- `version`: Version of the action (optional, default: latest)

#### `jvcli info agent`
Get information about an agent package.

```sh
jvcli info agent my_namespace/custom_agent
# With specific version
jvcli info agent my_namespace/custom_agent 1.0.0
```

Options:
- `name`: Name of the agent
- `version`: Version of the agent (optional, default: latest)

### Update Commands

#### `jvcli update namespace`
Update operations for a specified namespace.

```sh
# Invite a user to a namespace
jvcli update namespace my-namespace --invite user@example.com
# Transfer ownership of a namespace
jvcli update namespace my-namespace --transfer newowner@example.com
```

Options:
- `namespace`: Name of the namespace to update
- `--invite`: Invite a user to the namespace by their email
- `--transfer`: Transfer ownership of the namespace to a specified user by their email

### Server Commands

#### `jvcli server launch`
Launch the Jivas Server by running a JAC file.

```sh
jvcli server launch
# With custom JAC file
jvcli server launch --jac-file custom.jac
```

Options:
- `--jac-file`: Path to the JAC file to run (default: main.jac)

#### `jvcli server login`
Login to Jivas Server and get an authentication token.

```sh
jvcli server login
# With credentials
jvcli server login --email admin@example.com --password mypassword
```

Options:
- `--email`: Email address for Jivas login
- `--password`: Password for Jivas login

#### `jvcli server createadmin`
Create a system administrator account.

```sh
jvcli server createadmin
# With credentials
jvcli server createadmin --email admin@example.com --password mypassword
```

Options:
- `--email`: Email address for the system admin
- `--password`: Password for the system admin

#### `jvcli server initagents`
Initialize agents in the Jivas system.

```sh
jvcli server initagents
```

#### `jvcli server importagent`
Import an agent from a DAF package.

```sh
jvcli server importagent my_agent
# With specific version
jvcli server importagent my_agent 1.0.0
```

Options:
- `agent_name`: Name of the agent to import
- `version`: Version of the agent (optional, default: latest)

### Studio Commands

#### `jvcli studio launch`
Launch the Jivas Studio on a specified port.

```sh
jvcli studio launch
# With custom port
jvcli studio launch --port 9000
# With authentication required
jvcli studio launch --require-auth
```

Options:
- `--port`: Port for the studio to launch on (default: 8989)
- `--require-auth`: Require authentication for studio API (default: false)

### Client Commands

#### `jvcli client launch`
Launch the Jivas Client.

```sh
jvcli client launch
# With custom port
jvcli client launch --port 9001
# With custom Jivas and Studio URLs
jvcli client launch --jivas_url http://my-server:8000 --studio_url http://my-studio:8989
```

Options:
- `--port`: Port for the client to launch on (default: 8501)
- `--jivas_url`: URL for the Jivas API (default: http://localhost:8000 or JIVAS_BASE_URL env var)
- `--studio_url`: URL for the Jivas Studio (default: http://localhost:8989 or JIVAS_STUDIO_URL env var)

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
