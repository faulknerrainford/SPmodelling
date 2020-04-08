<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Socio-Physical Modelling Toolkit</title>
</head>
<body>
<h1>Socio-Physical Modelling Toolkit</h1>
<section>
<h2> Installation</h2>
    <article>
        To use the bash scripts provided to run the modelling in this package the package directory needs to be added
        to the system path.
    </article>
</section>
<section>
    <h2> Specification of a model</h2>
    <article>
        To specify a particular model create "specification.py" in this template:

            <p><code>
                import Model_agent as Agents<br>
                import Model_Balancer as Balancer<br>
                import Model_nodes as Nodes<br>
                import Model_Monitor as Monitor<br>
                import Model_Population as Population
            </code></p>
        Where each imported module contains a subclass of the respective SPmodelling Class.
        For instance Agents must contain an Agent class which is a subclass of the SPmodelling Agent Class.
        This will allow the modelling programs in SPmodelling to import the correct unique rules and agents for the
        model.
    </article>
</section>

</body>
</html>