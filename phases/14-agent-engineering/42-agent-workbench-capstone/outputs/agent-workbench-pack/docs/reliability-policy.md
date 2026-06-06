# Reliability Policy

Workbench endüstri-tekrarlayan beş failure mode'unu emer:

1. Hallucinated action — rule set + verification gate tarafından yakalanır.
2. Scope creep — scope kontratı diff check'i tarafından yakalanır.
3. Cascading errors — feedback kayıtları + refuse-on-null-exit tarafından yakalanır.
4. Context loss — repo memory tarafından emilir; chat source of truth değildir.
5. Tool misuse — reviewer rubric'in verification boyutu tarafından yakalanır.

Policy verification gate tarafından enforce edilir. Override yolu imzalı ve denetlenebilirdir; agent'lar kendilerini override edemez.
