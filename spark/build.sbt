val scala3Version = "3.5.2"

lazy val root = project
  .in(file("."))
  .settings(
    name := "spark",
    version := "0.1.0-SNAPSHOT",

    scalaVersion := scala3Version,

    libraryDependencies ++= Seq(
      "org.scalameta" %% "munit" % "1.0.0" % Test,
      ("org.apache.spark" %% "spark-core" % "3.3.2").cross(CrossVersion.for3Use2_13),
      ("org.apache.spark" %% "spark-sql" % "3.3.2").cross(CrossVersion.for3Use2_13),
      "org.postgresql" % "postgresql" % "42.2.20"
    )

  )



    