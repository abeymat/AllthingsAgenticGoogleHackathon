@isTest
private class StudentApplicationControllerTest {

    @TestSetup
    static void setupTestData() {
        List<Lead> testApplications = new List<Lead>();
        for (Integer i = 0; i < 5; i++) {
            testApplications.add(new Lead(
                FirstName = 'Student' + i,
                LastName = 'Applicant' + i,
                Email = 'student' + i + '@example.com',
                Phone = '555-010' + i,
                Company = 'Higher Education Prospect',
                Status = 'Open - Not Contacted',
                LeadSource = 'Web'
            ));
        }
        insert testApplications;
    }

    @isTest
    static void testSubmitApplicationSuccess() {
        Test.startTest();
        Lead result = StudentApplicationController.submitApplication(
            'Alex',
            'Smith',
            'alex.smith@example.com',
            '555-9876',
            'Higher Education Prospect'
        );
        Test.stopTest();

        System.assertNotEquals(null, result, 'Returned Lead record should not be null.');
        System.assertNotEquals(null, result.Id, 'Returned Lead should have a valid Salesforce Id.');

        Lead insertedLead = [SELECT Id, FirstName, LastName, Email, Phone, Company FROM Lead WHERE Id = :result.Id];
        System.assertEquals('Alex', insertedLead.FirstName, 'First name should match submitted value.');
        System.assertEquals('Smith', insertedLead.LastName, 'Last name should match submitted value.');
        System.assertEquals('alex.smith@example.com', insertedLead.Email, 'Email should match submitted value.');
    }

    @isTest
    static void testSubmitApplicationException() {
        Boolean exceptionThrown = false;

        Test.startTest();
        try {
            // Missing required LastName field to force DML exception
            StudentApplicationController.submitApplication('Alex', null, 'alex.smith@example.com', '555-9876', 'Higher Education Prospect');
        } catch (AuraHandledException e) {
            exceptionThrown = true;
        } catch (Exception e) {
            exceptionThrown = true;
        }
        Test.stopTest();

        System.assert(exceptionThrown, 'An exception should be caught when required fields are missing.');
    }

    @isTest
    static void testGetStudentApplications() {
        Test.startTest();
        List<Lead> applications = StudentApplicationController.getStudentApplications();
        Test.stopTest();

        System.assertEquals(5, applications.size(), 'Should retrieve all 5 seeded student application leads.');
    }

    @isTest
    static void testGetApplicationDetailsSuccess() {
        Lead existingLead = [SELECT Id, FirstName, LastName FROM Lead LIMIT 1];

        Test.startTest();
        Lead result = StudentApplicationController.getApplicationDetails(existingLead.Id);
        Test.stopTest();

        System.assertNotEquals(null, result, 'Application details should be returned.');
        System.assertEquals(existingLead.Id, result.Id, 'Retrieved Lead Id should match requested Id.');
        System.assertEquals(existingLead.FirstName, result.FirstName, 'Retrieved FirstName should match expected record.');
    }

    @isTest
    static void testGetApplicationDetailsInvalidId() {
        // Construct a non-existent Lead Id
        String fakeId = Lead.sObjectType.getDescribe().getKeyPrefix() + '000000000000AAA';
        Boolean exceptionThrown = false;

        Test.startTest();
        try {
            StudentApplicationController.getApplicationDetails((Id)fakeId);
        } catch (AuraHandledException e) {
            exceptionThrown = true;
        } catch (Exception e) {
            exceptionThrown = true;
        }
        Test.stopTest();

        System.assert(exceptionThrown, 'Exception should be thrown when querying with an invalid Record Id.');
    }
}