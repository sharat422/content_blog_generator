export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="space-y-8">
          {/* Page Header */}
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold text-foreground">Privacy Policy</h1>
          </div>

          {/* Sections */}
          <div className="prose prose-gray max-w-none space-y-8">
            <section className="space-y-4">
              <h2 className="text-2xl font-semibold text-foreground">1. Information We Collect</h2>
              <div className="text-muted-foreground leading-relaxed space-y-3">
                <p>We collect information you provide directly to us, such as when you:</p>
                <ul className="list-disc pl-6 space-y-1">
                  <li>Create an account or use our Service</li>
                  <li>Generate content using our tools</li>
                  <li>Contact us for support or inquiries</li>
                  <li>Subscribe to newsletters or updates</li>
                </ul>
                <p>
                  This may include personal information such as your name, email address, 
                  billing details (if applicable), and usage data related to how you interact 
                  with CreativeAI.
                </p>
              </div>
            </section>

            <section className="space-y-4">
              <h2 className="text-2xl font-semibold text-foreground">2. How We Use Your Information</h2>
              <div className="text-muted-foreground leading-relaxed space-y-2">
                <p>We use the information we collect to:</p>
                <ul className="list-disc pl-6 space-y-1">
                  <li>Provide, maintain, and improve the CreativeAI platform</li>
                  <li>Process transactions and manage your account</li>
                  <li>Send you technical notices, updates, and support messages</li>
                  <li>Respond to your questions and support requests</li>
                  <li>Monitor usage trends and improve functionality</li>
                  <li>Personalize your experience and content generation</li>
                </ul>
              </div>
            </section>

            <section className="space-y-4">
              <h2 className="text-2xl font-semibold text-foreground">3. Information Sharing and Disclosure</h2>
              <div className="text-muted-foreground leading-relaxed space-y-3">
                <p>We do not sell your personal information. We may share information only in these cases:</p>
                <ul className="list-disc pl-6 space-y-1">
                  <li><strong>With your consent:</strong> when you allow us explicitly</li>
                  <li><strong>Service providers:</strong> with trusted partners who support our operations</li>
                  <li><strong>Legal compliance:</strong> when required by law or valid legal process</li>
                  <li><strong>Business transfers:</strong> as part of a merger, acquisition, or sale of assets</li>
                </ul>
              </div>
            </section>

            <section className="space-y-4">
              <h2 className="text-2xl font-semibold text-foreground">4. Data Security</h2>
              <p className="text-muted-foreground leading-relaxed">
                We use reasonable technical and organizational measures to protect your data.
                However, no method of transmission or storage is completely secure.
              </p>
            </section>

            <section className="space-y-4">
              <h2 className="text-2xl font-semibold text-foreground">5. Data Retention</h2>
              <p className="text-muted-foreground leading-relaxed">
                We retain your data only as long as needed to provide the Service or as required by law.
                When no longer required, we will securely delete or anonymize it.
              </p>
            </section>

            <section className="space-y-4">
              <h2 className="text-2xl font-semibold text-foreground">6. Your Rights and Choices</h2>
              <div className="text-muted-foreground leading-relaxed space-y-2">
                <p>You may have rights depending on your jurisdiction:</p>
                <ul className="list-disc pl-6 space-y-1">
                  <li>Access and request a copy of your data</li>
                  <li>Correct inaccurate or incomplete information</li>
                  <li>Request deletion of your data</li>
                  <li>Request portability of your data</li>
                  <li>Opt out of marketing communications</li>
                </ul>
              </div>
            </section>

            <section className="space-y-4">
              <h2 className="text-2xl font-semibold text-foreground">7. Cookies and Tracking</h2>
              <p className="text-muted-foreground leading-relaxed">
                CreativeAI may use cookies and similar technologies to improve your user experience. 
                You can control cookies in your browser, but disabling them may affect the functionality of the Service.
              </p>
            </section>

            <section className="space-y-4">
              <h2 className="text-2xl font-semibold text-foreground">8. Children's Privacy</h2>
              <p className="text-muted-foreground leading-relaxed">
                CreativeAI is not intended for children under 13. We do not knowingly collect data 
                from children. If we become aware of such data, we will delete it promptly.
              </p>
            </section>

            <section className="space-y-4">
              <h2 className="text-2xl font-semibold text-foreground">9. Changes to This Policy</h2>
              <p className="text-muted-foreground leading-relaxed">
                We may update this Privacy Policy occasionally. Changes will be posted on this page with
                an updated "Last updated" date. Your continued use of CreativeAI constitutes acceptance of updates.
              </p>
            </section>

            <section className="space-y-4">
              <h2 className="text-2xl font-semibold text-foreground">10. Contact Us</h2>
              <p className="text-muted-foreground leading-relaxed">
                If you have questions about this Privacy Policy, contact us:
              </p>
              <div className="bg-muted/50 rounded-lg p-4">
                <p className="text-muted-foreground">
                  <strong>Email:</strong> creativeaimsr@gmail.com <br />
                </p>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
