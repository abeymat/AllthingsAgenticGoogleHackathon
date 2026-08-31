public with sharing class StudentApplicationController {

    @AuraEnabled
    public static String submitApplication(Map<String, Object> formData) {
        try {
            if (formData == null || formData.isEmpty()) {
                throw new AuraHandledException('Application form data cannot be empty.');
            }

            String firstName = (String) formData.get('firstName');
            String lastName = (String) formData.get('lastName');
            String email = (String) formData.get('email');
            String phone = (String) formData.get('phone');
            String major = (String) formData.get('major');
            Decimal gpa = formData.get('gpa') != null ? Decimal.valueOf(String.valueOf(formData.get('gpa'))) : null;
            String scholarshipType = (String) formData.get('scholarshipType');
            String statementOfPurpose = (String) formData.get('statementOfPurpose');

            if (String.isBlank(lastName) || String.isBlank(email)) {
                throw new AuraHandledException('Last Name and Email are required fields.');
            }

            if (!Schema.sObjectType.Contact.isCreateable()) {
                throw new AuraHandledException('Insufficient permissions to create student application records.');
            }

            // Map fields to standard Contact object for high org compatibility
            Contact applicant = new Contact();
            applicant.FirstName = firstName;
            applicant.LastName = lastName;
            applicant.Email = email;
            applicant.Phone = phone;

            String descriptionDetails = 'Scholarship Application Details:\n' +
                '-----------------------------\n' +
                'Intended Major: ' + (String.isNotBlank(major) ? major : 'N/A') + '\n' +
                'Current GPA: ' + (gpa != null ? String.valueOf(gpa) : 'N/A') + '\n' +
                'Scholarship Type: ' + (String.isNotBlank(scholarshipType) ? scholarshipType : 'N/A') + '\n\n' +
                'Statement of Purpose:\n' + (String.isNotBlank(statementOfPurpose) ? statementOfPurpose : 'N/A');

            applicant.Description = descriptionDetails;

            insert applicant;
            return applicant.Id;

        } catch (AuraHandledException e) {
            throw e;
        } catch (Exception e) {
            throw new AuraHandledException('An error occurred while processing your application: ' + e.getMessage());
        }
    }
}