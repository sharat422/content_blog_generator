export default function TermsOfService() {
  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="space-y-8">
          {/* Page Header */}
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold text-foreground">Terms of Service</h1>
          </div>

          {/* Sections */}
          <div className="prose prose-gray max-w-none space-y-8">
            <section className="space-y-4">
              <h2 className="text-2xl font-semibold text-foreground">1. Acceptance of Terms</h2>
              <p className="text-muted-foreground leading-relaxed">
                By accessing and using CreativeAI ("the Service"), you agree to be bound by these Terms of Service. 
                If you do not agree, you may not use the Service.
              </p>
            </section>

            <section className="space-y-4">
              <h2 className="text-2xl font-semibold text-foreground">2. Description of Service</h2>
              <p className="text-muted-foreground leading-relaxed">
                CreativeAI is a content and blog generation platform that leverages artificial intelligence to help
                users create blog posts, product descriptions, social media content, and other written material quickly
                and efficiently.
              </p>
            </section>

            <section className="space-y-4">
              <h2 className="text-2xl font-semibold text-foreground">3. User Accounts</h2>
              <p className="text-muted-foreground leading-relaxed">
                To access certain features, you may be required to create an account. You are responsible for maintaining
                the confidentiality of your login credentials and all activities under your account.
              </p>
            </section>

            <section className="space-y-4">
              <h2 className="text-2xl font-semibold text-foreground">4. Acceptable Use</h2>
              <div className="text-muted-foreground leading-relaxed space-y-2">
                <p>When using CreativeAI, you agree not to:</p>
                <ul className="list-disc pl-6 space-y-1">
                  <li>Use the Service in any way that violates applicable laws or regulations.</li>
                  <li>Submit or generate unlawful, harmful, or defamatory content.</li>
                  <li>Attempt to gain unauthorized access to the Service or its systems.</li>
                  <li>Interfere with or disrupt the Service or its infrastructure.</li>
                </ul>
              </div>
            </section>

            <section className="space-y-4">
              <h2 className="text-2xl font-semibold text-foreground">5. Data and Privacy</h2>
              <p className="text-muted-foreground leading-relaxed">
                Your privacy is important to us. Please review our Privacy Policy for details on how we collect, 
                use, and protect your information.
              </p>
            </section>

            <section className="space-y-4">
              <h2 className="text-2xl font-semibold text-foreground">6. Limitation of Liability</h2>
              <p className="text-muted-foreground leading-relaxed">
                CreativeAI shall not be held liable for any indirect, incidental, or consequential damages, 
                including but not limited to loss of data, profits, or business opportunities resulting from 
                the use of the Service.
              </p>
            </section>

            <section className="space-y-4">
              <h2 className="text-2xl font-semibold text-foreground">7. Termination</h2>
              <p className="text-muted-foreground leading-relaxed">
                We may suspend or terminate your access to the Service at our sole discretion, without prior notice, 
                if you violate these Terms.
              </p>
            </section>

            <section className="space-y-4">
              <h2 className="text-2xl font-semibold text-foreground">8. Changes to Terms</h2>
              <p className="text-muted-foreground leading-relaxed">
                We may update these Terms from time to time. Any changes will be effective immediately upon posting. 
                Continued use of the Service constitutes acceptance of the updated Terms.
              </p>
            </section>

            <section className="space-y-4">
              <h2 className="text-2xl font-semibold text-foreground">9. Contact Information</h2>
              <p className="text-muted-foreground leading-relaxed">
                For questions regarding these Terms of Service, please contact us:
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
