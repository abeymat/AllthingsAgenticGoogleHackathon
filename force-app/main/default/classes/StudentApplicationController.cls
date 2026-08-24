public with sharing class StudentApplicationController {

    public class ApplicationWrapper {
        @AuraEnabled public String id { get; set; }
        @AuraEnabled public String firstName { get; set; }
        @AuraEnabled public String lastName { get; set; }
        @AuraEnabled public String email { get; set; }
        @AuraEnabled public String phone { get; set; }
        @AuraEnabled public String status { get; set; }
        @AuraEnabled public String program { get; set; }
        @AuraEnabled public Datetime createdDate { get; set; }
    }

    /**
     * @description Submits a new student application as a Lead record.
     * @param firstName Student's first name
     * @param lastName Student's last name
     * @param email Student's email address
     * @param phone Student's phone number
     * @param program Program of interest
     * @return Id of the created/updated Lead record
     */
    @AuraEnabled
    public static Id submitApplication(String firstName, String lastName, String email, String phone, String program) {
        try {
            if (String.isBlank(lastName) || String.isBlank(email)) {
                throw new AuraHandledException('Last Name and Email are required fields.');
            }

            // Check for existing applicant by email
            List<Lead> existingLeads = [
                SELECT Id, FirstName, LastName, Email, Phone, Description, Status
                FROM Lead
                WHERE Email = :email
                WITH USER_MODE
                LIMIT 1
            ];

            Lead studentLead;
            if (!existingLeads.isEmpty()) {
                studentLead = existingLeads[0];
                studentLead.FirstName = firstName;
                studentLead.LastName = lastName;
                studentLead.Phone = phone;
                studentLead.Description = 'Program of Interest: ' + (String.isNotBlank(program) ? program : 'General');
                update as user studentLead;
            } else {
                studentLead = new Lead(
                    FirstName = firstName,
                    LastName = lastName,
                    Email = email,
                    Phone = phone,
                    Company = 'Student Applicant',
                    Status = 'Open - Not Contacted',
                    LeadSource = 'Web',
                    Description = 'Program of Interest: ' + (String.isNotBlank(program) ? program : 'General')
                );
                insert as user studentLead;
            }

            return studentLead.Id;
        } catch (AuraHandledException e) {
            throw e;
        } catch (Exception ex) {
            throw new AuraHandledException('Failed to submit application: ' + ex.getMessage());
        }
    }

    /**
     * @description Retrieves recent student applications.
     * @param recordLimit Maximum number of records to return
     * @return List of ApplicationWrapper objects
     */
    @AuraEnabled(cacheable=true)
    public static List<ApplicationWrapper> getRecentApplications(Integer recordLimit) {
        try {
            Integer queryLimit = (recordLimit != null && recordLimit > 0) ? recordLimit : 50;

            List<Lead> leads = [
                SELECT Id, FirstName, LastName, Email, Phone, Status, Description, CreatedDate
                FROM Lead
                WHERE Company = 'Student Applicant'
                WITH USER_MODE
                ORDER BY CreatedDate DESC
                LIMIT :queryLimit
            ];

            List<ApplicationWrapper> applications = new List<ApplicationWrapper>();
            for (Lead l : leads) {
                ApplicationWrapper app = new ApplicationWrapper();
                app.id = l.Id;
                app.firstName = l.FirstName;
                app.lastName = l.LastName;
                app.email = l.Email;
                app.phone = l.Phone;
                app.status = l.Status;
                app.program = l.Description;
                app.createdDate = l.CreatedDate;
                applications.add(app);
            }

            return applications;
        } catch (Exception ex) {
            throw new AuraHandledException('Error fetching applications: ' + ex.getMessage());
        }
    }

    /**
     * @description Fetches application status by email address.
     * @param email Student email address
     * @return ApplicationWrapper with current status details
     */
    @AuraEnabled(cacheable=true)
    public static ApplicationWrapper getApplicationStatusByEmail(String email) {
        try {
            if (String.isBlank(email)) {
                throw new AuraHandledException('Email is required to check application status.');
            }

            List<Lead> leads = [
                SELECT Id, FirstName, LastName, Email, Phone, Status, Description, CreatedDate
                FROM Lead
                WHERE Email = :email AND Company = 'Student Applicant'
                WITH USER_MODE
                ORDER BY CreatedDate DESC
                LIMIT 1
            ];

            if (leads.isEmpty()) {
                return null;
            }

            Lead l = leads[0];
            ApplicationWrapper app = new ApplicationWrapper();
            app.id = l.Id;
            app.firstName = l.FirstName;
            app.lastName = l.LastName;
            app.email = l.Email;
            app.phone = l.Phone;
            app.status = l.Status;
            app.program = l.Description;
            app.createdDate = l.CreatedDate;

            return app;
        } catch (AuraHandledException e) {
            throw e;
        } catch (Exception ex) {
            throw new AuraHandledException('Error retrieving status: ' + ex.getMessage());
        }
    }
}