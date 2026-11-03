ThisBuild / scalaVersion := "3.3.4"

lazy val root = (project in file("."))
  .settings(
    name := "soporte360-scala",
    version := "1.0.0",
    Compile / run / fork := true,
    Compile / run / connectInput := true,
    Compile / mainClass := Some("soporte360.Main")
  )
