workflow "generate data.json other files." {
  on = "push"
  resolves = [
    "Generate"
  ]
}

action "Build image" {
  uses = "actions/docker/cli"
  args = [
    "build --tag=repo:latest ."
  ]
}
