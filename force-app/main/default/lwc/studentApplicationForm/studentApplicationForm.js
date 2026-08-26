import { LightningElement, track, api } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

export default class StudentApplicationForm extends LightningElement {
    @api recordId;
    @api objectApiName;

    @track firstName = '';
    @track lastName = '';
    @track email = '';
    @track phone = '';
    @track company = '';
    @track isLoading = false;

    handleInputChange(event) {
        const fieldName = event.target.name;
        const fieldValue = event.target.value;

        if (fieldName === 'firstName') {
            this.firstName = fieldValue;
        } else if (fieldName === 'lastName') {
            this.lastName = fieldValue;
        } else if (fieldName === 'email') {
            this.email = fieldValue;
        } else if (fieldName === 'phone') {
            this.phone = fieldValue;
        } else if (fieldName === 'company') {
            this.company = fieldValue;
        }
    }

    handleSubmit(event) {
        event.preventDefault();
        
        const allValid = [...this.template.querySelectorAll('lightning-input')]
            .reduce((validSoFar, inputCmp) => {
                inputCmp.reportValidity();
                return validSoFar && inputCmp.checkValidity();
            }, true);

        if (!allValid) {
            this.showToast('Error', 'Please complete all required fields correctly.', 'error');
            return;
        }

        this.isLoading = true;

        const applicationData = {
            firstName: this.firstName,
            lastName: this.lastName,
            email: this.email,
            phone: this.phone,
            company: this.company
        };

        const submitEvent = new CustomEvent('applicationsubmit', {
            detail: applicationData
        });
        this.dispatchEvent(submitEvent);

        this.showToast('Success', 'Student application submitted successfully!', 'success');
        this.handleReset();
        this.isLoading = false;
    }

    handleReset() {
        this.firstName = '';
        this.lastName = '';
        this.email = '';
        this.phone = '';
        this.company = '';

        const inputFields = this.template.querySelectorAll('lightning-input');
        if (inputFields) {
            inputFields.forEach(field => {
                field.value = '';
            });
        }
    }

    showToast(title, message, variant) {
        const evt = new ShowToastEvent({
            title: title,
            message: message,
            variant: variant
        });
        this.dispatchEvent(evt);
    }
}