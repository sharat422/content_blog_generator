export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="space-y-8">

          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold text-foreground">Privacy Policy</h1>
          </div>

          <div className="prose prose-gray max-w-none space-y-8">

            <section>
              <h2 className="text-2xl font-semibold text-foreground">1. Information We Collect</h2>
              <p className="text-muted-foreground leading-relaxed">
                We collect information you provide when you use WriteSwift, including:
              </p>
              <ul className="list-disc pl-6 text-muted-foreground space-y-1">
                <li>Account details (email, name)</li>
                <li>Content you input (text, prompts, uploaded files)</li>
                <li>AI-generated content</li>
                <li>Interaction history with the Synth Twin</li>
                <li>Stored memories (preferences, goals, prior messages)</li>
                <li>Billing information (processed securely by Stripe)</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">2. How We Use Your Information</h2>
              <p className="text-muted-foreground leading-relaxed">
                We use your data to:
              </p>
              <ul className="list-disc pl-6 text-muted-foreground space-y-1">
                <li>Operate and improve the platform</li>
                <li>Personalize your AI experience through the Synth Twin</li>
                <li>Store memory for future interactions at your request</li>
                <li>Process transactions and manage subscriptions</li>
                <li>Generate AI-based content using your input</li>
                <li>Detect misuse or harmful activity</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">3. Synth Twin Memory and Stored Data</h2>
              <p className="text-muted-foreground leading-relaxed">
                Your interactions with the Synth Twin may be stored to improve personalization.
                This includes preferences, previous messages, goals, and generated content.
              </p>
              <p className="text-muted-foreground leading-relaxed">
                You may request deletion of your stored memories at any time by contacting support.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">4. Information Sharing</h2>
              <p className="text-muted-foreground leading-relaxed">We do not sell your personal data. We may share data only in the following cases:</p>
              <ul className="list-disc pl-6 text-muted-foreground space-y-1">
                <li><strong>Service Providers:</strong> such as hosting, analytics, AI model providers, and billing partners like Stripe.</li>
                <li><strong>Legal compliance:</strong> when required by law or legal obligation.</li>
                <li><strong>Business transfers:</strong> in the event of acquisition or restructuring.</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">5. Data Security</h2>
              <p className="text-muted-foreground leading-relaxed">
                We use industry-standard security practices. However, no method of storing or transmitting information is completely secure, and we cannot guarantee absolute security.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">6. Data Retention</h2>
              <p className="text-muted-foreground leading-relaxed">
                We retain your data as long as necessary to provide the Service or comply with legal obligations.
                You may request deletion or export of your data.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">7. Third-Party AI Providers</h2>
              <p className="text-muted-foreground leading-relaxed">
                Some AI features may be powered by third-party large-language model providers.
                Your prompts and generated content may be processed by such services solely to provide the requested response.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">8. Cookies & Tracking Technologies</h2>
              <p className="text-muted-foreground leading-relaxed">
                We may use cookies to maintain sessions, analyze usage, and improve your experience.
                You may disable cookies, but certain features may not function.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">9. Children's Privacy</h2>
              <p className="text-muted-foreground leading-relaxed">
                The Service is not intended for children under 13, and we do not knowingly collect information from them.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">10. Changes to This Policy</h2>
              <p className="text-muted-foreground leading-relaxed">
                We may update this Privacy Policy periodically. Continued use constitutes acceptance of changes.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-foreground">11. Contact Us</h2>
              <div className="bg-muted/50 rounded-lg p-4">
                <strong>Email:</strong> creativeaimsr@gmail.com
              </div>
            </section>

          </div>
        </div>
      </div>
    </div>
  );
}
