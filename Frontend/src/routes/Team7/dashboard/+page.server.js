export function load() {
  return {
      projectName: "Project 1",
      tools: [
          { name: "Crawler",  route: "/crawler/config" },
          { name: "Fuzzer", route: "/fuzzer/config" },
          { name: "Brute Force", route: "/bruteForce/config" },
      ],
  };
}
