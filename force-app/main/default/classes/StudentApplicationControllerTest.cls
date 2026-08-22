@isTest
private class StudentApplicationControllerTest {

    @TestSetup
    static void setupTestData() {
        List<Lead> testApplications = new List<Lead>();
        for (Integer i = 0; i < 5; i++) {
            testApplications.add(new Lead(
                FirstName = 'TestStudent',
                LastName = 'Applicant ' + i,
                Company = 'Applicant Self',
                Email = 'student' + i + '@example.com',
                Phone = '555000000' + i,
                Status = 'Open - Not Contacted'
            ));
        }
        insert testApplications;
    }

    @isTest
    static void testGetStudentApplicationsSuccess() {
        Test.startTest();
        List<Lead> results = StudentApplicationController.getStudentApplications();
        Test.stopTest();

        Assert.isNotNull(results, 'Results list should not be null.');
        Assert.areEqual(5, results.size(), 'Expected 5 student application records to be retrieved.');
    }

    @isTest
    static void testSubmitApplicationSuccess() {
        Lead newApplicant = new Lead(
            FirstName = 'Jane',
            LastName = 'Doe',
            Company = 'Applicant Self',
            Email = 'jane.doe@example.com',
            Phone = '5551234567'
        );

        Test.startTest();
        Lead insertedApplicant = StudentApplicationController.submitApplication(newApplicant);
        Test.stopTest();

        Assert.isNotNull(insertedApplicant, 'Inserted applicant record should not be null.');
        Assert.isNotNull(insertedApplicant.Id, 'Inserted applicant should have a valid Salesforce ID.');
        Assert.areEqual('Jane', insertedApplicant.FirstName, 'First name should match.');
        Assert.areEqual('Doe', insertedApplicant.LastName, 'Last name should match.');
    }

    @isTest
    static void testSubmitApplicationException() {
        // Omitting required field 'LastName' to trigger exception
        Lead invalidApplicant = new Lead(
            FirstName = 'InvalidApplicant'
        );

        Boolean exceptionThrown = false;

        Test.startTest();
        try {
            StudentApplicationController.submitApplication(invalidApplicant);
        } catch (AuraHandledException e) {
            exceptionThrown = true;
        } catch (Exception e) {
            exceptionThrown = true;
        }
        Test.stopTest();

        Assert.isTrue(exceptionThrown, 'An exception should be thrown when attempting to insert an invalid record.');
    }

    @isTest
    static void testUpdateApplicationStatusSuccess() {
        Lead existingApplicant = [SELECT Id, Status FROM Lead WHERE Email = 'student0@example.com' LIMIT 1];
        String updatedStatus = 'Working - Contacted';

        Test.startTest();
        Lead result = StudentApplicationController.updateApplicationStatus(existingApplicant.Id, updatedStatus);
        Test.stopTest();

        Assert.isNotNull(result, 'Result should not be null.');
        Assert.areEqual(updatedStatus, result.Status, 'Status should be successfully updated.');
    }

    @isTest
    static void testUpdateApplicationStatusException() {
        Boolean exceptionThrown = false;

        Test.startTest();
        try {
            StudentApplicationController.updateApplicationStatus(null, 'Working - Contacted');
        } catch (AuraHandledException e) {
            exceptionThrown = true;
        } catch (Exception e) {
            exceptionThrown = true;
        }
        Test.stopTest();

        Assert.isTrue(exceptionThrown, 'An exception should be thrown when an invalid Record Id is provided.');
    }
}