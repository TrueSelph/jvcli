# Getting Started with JIVAS

Welcome to your JIVAS AI project boilerplate!

## Running Your JIVAS App

To start your JIVAS app, execute the following command within this project folder:

```sh
sh sh/serve.sh
```

## Setting Up a Demo Agent

To set up a demo agent, run the following command in another terminal:

```sh
sh sh/importagent.sh jivas/demo_ai
```

This will initialize JIVAS, download, and install a demo agent. If you wish to install any other agent, replace 'jivas/demo_ai' with the package name of your agent's DAF.

## Accessing the JIVAS Manager

Once the setup is complete, run the following command in its own terminal to access the JIVAS manager for configuring and chatting with your agent:

```sh
sh sh/startclient.sh
```

## Reflecting Changes to Agent Actions

If you make any changes to the agent actions, run the following command to reinitialize all agents running within this JIVAS app:

```sh
sh sh/initagents.sh
```

## Logging In

When the JIVAS manager loads, log in with the default JIVAS credentials found in your `.env` file.

Happy building!